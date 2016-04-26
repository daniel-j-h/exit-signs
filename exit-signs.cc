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


struct ExitSignHandler final : osmium::handler::Handler {
  void node(const osmium::Node& node) { (void)node; }

  void way(const osmium::Way& way) {
    const auto* highway = way.get_value_by_key("highway");
    if (!highway)
      return;

    const auto* ref = way.get_value_by_key("ref");

    const auto* destination = way.get_value_by_key("destination");
    const auto* destination_fwd = way.get_value_by_key("destination:forward");
    const auto* destination_bkw = way.get_value_by_key("destination:backward");

    const auto I = [](const auto* s){ return s ? s : ""; };

#ifndef NDEBUG
    std::printf("Highway: %s, Ref: %s, Dst: %s, DstFwd: %s, DstBkw: %s\n",
        I(highway), I(ref), I(destination), I(destination_fwd), I(destination_bkw));
#endif

    if (destination)
      for (const auto& node : way.nodes())
        std::printf("%f,%f\n", node.location().lon(), node.location().lat());

    (void)highway;
    (void)ref;
    (void)destination;
    (void)destination_fwd;
    (void)destination_bkw;
    (void)I;
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
