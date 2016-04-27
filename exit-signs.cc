#include <cstdlib>
#include <cstring>

#include <algorithm>
#include <ios>
#include <iterator>
#include <locale>
#include <stdexcept>
#include <string>
#include <vector>

#include <osmium/handler.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/index/map/sparse_mem_array.hpp>
#include <osmium/io/pbf_input.hpp>
#include <osmium/io/reader.hpp>
#include <osmium/osm/types.hpp>
#include <osmium/visitor.hpp>

using PositiveIndex = osmium::index::map::SparseMemArray<osmium::unsigned_object_id_type, osmium::Location>;
using LocationHandler = osmium::handler::NodeLocationsForWays<PositiveIndex>;


static auto I(const char* s){ return s ? s : ""; }


struct ExitSignHandler final : osmium::handler::Handler {
  void node(const osmium::Node& node) {
    const auto* ref = node.get_value_by_key("ref");
    const auto* name = node.get_value_by_key("name");
    const auto* exit_to = node.get_value_by_key("exit_to");

#ifndef NDEBUG
    std::printf("Node: %s, Ref: %s, ExitTo: %s\n",
        I(name), I(ref), I(exit_to));
#endif

    if (exit_to)
      std::printf("%.5f,%.5f\n", node.location().lon(), node.location().lat());
  }

  void way(const osmium::Way& way) {
    const auto* highway = way.get_value_by_key("highway");
    if (!highway)
      return;

    const auto* ref = way.get_value_by_key("ref");

    const auto* destination = way.get_value_by_key("destination");
    const auto* destination_ref = way.get_value_by_key("destination:ref");

#ifndef NDEBUG
    std::printf("Way: %s, Ref: %s, Dst: %s, DstRef: %s\n",
        I(highway), I(ref), I(destination), I(destination_ref));
#endif

    if (destination)
      for (const auto& node : way.nodes())
        std::printf("%.5f,%.5f\n", node.location().lon(), node.location().lat());
  }
};


int main(int argc, char** argv) try {
  std::locale::global(std::locale(""));
  std::ios_base::sync_with_stdio(false);

  if (argc != 2) {
    std::fprintf(stderr, "Usage: %s in.osm.pbf\n", argv[0]);
    return EXIT_FAILURE;
  }

  const auto entities = osmium::osm_entity_bits::nwr;
  osmium::io::Reader reader(argv[1], entities);

  PositiveIndex positiveIndex;
  LocationHandler locationHandler{positiveIndex};

  ExitSignHandler exitSignHandler;

  osmium::apply(reader, locationHandler, exitSignHandler);

} catch (const std::exception& e) {
  std::fprintf(stderr, "Error: %s\n", e.what());
  return EXIT_FAILURE;
}
