// Minimal subscriber to print custom gtec_msgs::msgs::Ranging messages.
// Provided as an example consumer of the plugin's output. `gz topic -e` can
// also echo the topic once GZ_DESCRIPTOR_PATH points at the build folder (see
// README); this binary links the generated ranging.pb.h directly, so it needs
// no descriptor env var and prints a compact, unit-labelled line per message.
// Build: cmake --build build --target echo_ranging
// Run:   ./build/echo_ranging
#include <iostream>
#include <gz/transport/Node.hh>
#include <gtec_msgs/msgs/ranging.pb.h>

static void OnRanging(const gtec_msgs::msgs::Ranging &msg)
{
  std::cout << "anchor_id=" << msg.anchor_id()
            << "  tag_id=" << msg.tag_id()
            << "  range=" << msg.range() << " mm"
            << "  rss=" << msg.rss() << " dB"
            << "  seq=" << msg.seq()
            << "  angle=" << msg.angle() << " rad"
            << "  err=" << msg.error_estimation()
            << std::endl;
}

int main()
{
  gz::transport::Node node;
  const std::string topic = "/gtec/toa/ranging";
  if (!node.Subscribe(topic, OnRanging))
  {
    std::cerr << "Failed to subscribe to " << topic << std::endl;
    return 1;
  }
  std::cout << "Listening on " << topic << " ... (Ctrl-C to stop)" << std::endl;
  gz::transport::waitForShutdown();
  return 0;
}
