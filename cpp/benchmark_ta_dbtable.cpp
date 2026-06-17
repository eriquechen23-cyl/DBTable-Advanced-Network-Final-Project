#include <chrono>
#include <bitset>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>
#include <vector>

#include "DBT_core.hpp"

uint32_t DBT::maskBit[33] = {
    0,          0x80000000, 0xC0000000, 0xE0000000, 0xF0000000, 0xF8000000,
    0xFC000000, 0xFE000000, 0xFF000000, 0xFF800000, 0xFFC00000, 0xFFE00000,
    0xFFF00000, 0xFFF80000, 0xFFFC0000, 0xFFFE0000, 0xFFFF0000, 0xFFFF8000,
    0xFFFFC000, 0xFFFFE000, 0xFFFFF000, 0xFFFFF800, 0xFFFFFC00, 0xFFFFFE00,
    0xFFFFFF00, 0xFFFFFF80, 0xFFFFFFC0, 0xFFFFFFE0, 0xFFFFFFF0, 0xFFFFFFF8,
    0xFFFFFFFC, 0xFFFFFFFE, 0xFFFFFFFF};

uint32_t DBT::getBit[32] = {
    0x80000000, 0x40000000, 0x20000000, 0x10000000, 0x08000000, 0x04000000,
    0x02000000, 0x01000000, 0x00800000, 0x00400000, 0x00200000, 0x00100000,
    0x00080000, 0x00040000, 0x00020000, 0x00010000, 0x00008000, 0x00004000,
    0x00002000, 0x00001000, 0x00000800, 0x00000400, 0x00000200, 0x00000100,
    0x00000080, 0x00000040, 0x00000020, 0x00000010, 0x00000008, 0x00000004,
    0x00000002, 0x00000001};

namespace {

uint32_t ipv4_to_u32(const std::string& ip) {
  std::stringstream ss(ip);
  std::string part;
  uint32_t value = 0;
  for (int i = 0; i < 4; ++i) {
    std::getline(ss, part, '.');
    value = (value << 8) | static_cast<uint32_t>(std::stoul(part));
  }
  return value;
}

bool load_rules(const std::string& path, std::vector<DBT::Rule>& rules) {
  std::ifstream in(path);
  if (!in) return false;
  std::regex rule_re(
      R"(^@([0-9.]+)/(\d+)\s+([0-9.]+)/(\d+)\s+(\d+)\s*:\s*(\d+)\s+(\d+)\s*:\s*(\d+)\s+(0x[0-9a-fA-F]+)/(0x[0-9a-fA-F]+))");
  std::string line;
  uint32_t priority = 0;
  while (std::getline(in, line)) {
    std::smatch match;
    if (!std::regex_search(line, match, rule_re)) continue;
    DBT::Rule rule{};
    rule.pri = priority++;
    rule.ip.i_32.sip = ipv4_to_u32(match[1]);
    rule.sip_length = static_cast<uint8_t>(std::stoul(match[2]));
    rule.ip.i_32.dip = ipv4_to_u32(match[3]);
    rule.dip_length = static_cast<uint8_t>(std::stoul(match[4]));
    rule.Port[0][0] = static_cast<uint16_t>(std::stoul(match[5]));
    rule.Port[0][1] = static_cast<uint16_t>(std::stoul(match[6]));
    rule.Port[1][0] = static_cast<uint16_t>(std::stoul(match[7]));
    rule.Port[1][1] = static_cast<uint16_t>(std::stoul(match[8]));
    rule.protocol.val = static_cast<uint8_t>(std::stoul(match[9], nullptr, 16));
    rule.protocol.mask = static_cast<uint8_t>(std::stoul(match[10], nullptr, 16));
    rule.mask.i_32.smask = DBT::maskBit[rule.sip_length];
    rule.mask.i_32.dmask = DBT::maskBit[rule.dip_length];
    rules.push_back(rule);
  }
  return true;
}

bool load_packets(const std::string& path, std::vector<DBT::Packet>& packets,
                  size_t limit) {
  std::ifstream in(path);
  if (!in) return false;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty()) continue;
    std::stringstream ss(line);
    uint64_t sip = 0, dip = 0;
    uint32_t sport = 0, dport = 0, proto = 0;
    if (!(ss >> sip >> dip >> sport >> dport >> proto)) continue;
    DBT::Packet packet{};
    packet.ip.i_32.sip = static_cast<uint32_t>(sip);
    packet.ip.i_32.dip = static_cast<uint32_t>(dip);
    packet.Port[0] = static_cast<uint16_t>(sport);
    packet.Port[1] = static_cast<uint16_t>(dport);
    packet.protocol = proto;
    packets.push_back(packet);
    if (limit != 0 && packets.size() >= limit) break;
  }
  return true;
}

size_t estimate_memory(const DBT::DBTable& table) {
  size_t mem = sizeof(DBT::SubSet) + table.subsets.size * sizeof(DBT::ip_node);
  for (int i = 0; i < table.subsets.size; ++i) {
    const auto& node = table.subsets.ipNodes[i];
    if (node.pri != 0xFFFFFFFF) {
      mem += node.tuples.size() * sizeof(DBT::Tuple);
      for (const auto& tuple : node.tuples) {
        for (int j = 0; j < tuple.mask + 1; ++j) {
          const DBT::prefix_tuple* ptuple = &tuple.ptuples[j];
          if (ptuple->pri == 0xFFFFFFFF) {
            mem += sizeof(DBT::prefix_tuple);
            continue;
          }
          while (ptuple != nullptr) {
            mem += sizeof(DBT::prefix_tuple);
            for (int k = 0; k < 2; ++k) {
              if (ptuple->pNodes[k] != nullptr) {
                std::bitset<16> bits = ptuple->pNodes[k]->mask;
                int pn_size = 1 << bits.count();
                mem += sizeof(DBT::port_node) + pn_size * sizeof(DBT::Bucket);
              }
            }
            ptuple = ptuple->next;
          }
        }
      }
    }
    if (node.prefix_down != nullptr) mem += (2178 * sizeof(char));
  }
  return mem;
}

}  // namespace

int main(int argc, char** argv) {
  std::string rules_path = "data/classbench/acl1_100000.txt";
  std::string trace_path = "data/classbench/acl1_100000.txt_trace";
  size_t max_packets = 100000;
  int threshold = 8;
  if (argc > 1) rules_path = argv[1];
  if (argc > 2) trace_path = argv[2];
  if (argc > 3) max_packets = static_cast<size_t>(std::stoull(argv[3]));
  if (argc > 4) threshold = std::stoi(argv[4]);

  std::vector<DBT::Rule> rules;
  std::vector<DBT::Packet> packets;
  if (!load_rules(rules_path, rules)) {
    std::cerr << "failed to load rules: " << rules_path << "\n";
    return 2;
  }
  if (!load_packets(trace_path, packets, max_packets)) {
    std::cerr << "failed to load packets: " << trace_path << "\n";
    return 2;
  }

  auto build_start = std::chrono::steady_clock::now();
  DBT::DBTable classifier(rules, threshold);
  classifier.construct();
  auto build_end = std::chrono::steady_clock::now();

  uint64_t matched = 0;
  auto lookup_start = std::chrono::steady_clock::now();
  for (const auto& packet : packets) {
    if (classifier.search(packet) != 0xFFFFFFFF) ++matched;
  }
  auto lookup_end = std::chrono::steady_clock::now();

  const double build_seconds =
      std::chrono::duration<double>(build_end - build_start).count();
  const double lookup_seconds =
      std::chrono::duration<double>(lookup_end - lookup_start).count();
  const double avg_lookup_ns =
      packets.empty() ? 0.0 : lookup_seconds * 1e9 / packets.size();
  const size_t memory_bytes = estimate_memory(classifier);

  std::cout << std::fixed << std::setprecision(9);
  std::cout << "{\n";
  std::cout << "  \"implementation\": \"TA DBTable.cpp\",\n";
  std::cout << "  \"rules_loaded\": " << rules.size() << ",\n";
  std::cout << "  \"packets_tested\": " << packets.size() << ",\n";
  std::cout << "  \"matched_packets\": " << matched << ",\n";
  std::cout << "  \"threshold\": " << threshold << ",\n";
  std::cout << "  \"build_seconds\": " << build_seconds << ",\n";
  std::cout << "  \"lookup_total_seconds\": " << lookup_seconds << ",\n";
  std::cout << "  \"lookup_avg_ns\": " << avg_lookup_ns << ",\n";
  std::cout << "  \"estimated_memory_bytes\": " << memory_bytes << ",\n";
  std::cout << "  \"estimated_memory_mib\": "
            << (memory_bytes / 1024.0 / 1024.0) << "\n";
  std::cout << "}\n";
  return 0;
}
