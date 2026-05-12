# PX4-gazebo-models
Models and worlds to be used in local Fuel instances and kept up to date in [app.gazebosim.org/PX4](https://app.gazebosim.org/PX4).

## Starting GZ simulation
In addition to providing resource files for all models and worlds, this repo also contains a simulation-gazebo script that will start a world and works in conjunction with PX4.

In order for this script to work, you must have installed gz-garden beforehand. The way to do this can be found [here](https://gazebosim.org/docs/garden/install_ubuntu):

After setting up gazebo, navigate to the repo containing simulation-gazebo and script with

```shell
python simulation-gazebo
```

If you do not provide any arguments, this will download all models and worlds from the PX4-gazebo-models repo, save them to `/.simulation-gazebo` and start a default world. **In order for a model to load, you need to start PX4 as well**

The following arguments can be passed:

`--world` A string variable that names the sdf file which runs the simulation world. Default argument is "default", which links to the default world.

`--gz_partition` A string variable that sets the gazebo partition to run in (more information [here]([https://gazebosim.org/api/transport/13/envvars.html))

`--gz_ip` A string variable that sets the IP of the outgoing network interface (more information [here]([https://gazebosim.org/api/transport/13/envvars.html))

`--interactive` A boolean variable that requires the ability to run the code in interactive mode, allowing for custom paths for `--model_download_source`. If this is not set, `--model_download_source` will only download from the default Github repo.

`--model_download_source` A string variable setting the path to a directory from where models are to be imported. At the moment this can only be a local file directory or a http address. The source should end with the zipped resource file. (e.g. https://path/to/simulation/models/resource.zip)

`--model_store` A string variable setting the path to the model storage directory. This is where the zip file provided in `model_download_source` will be placed.

`--overwrite` A boolean variable providing the ability to overwrite existing directories with new data.

`--dryrun` A boolean variable that can be set when running testcases. It will not provide any interactivity and will not start Gazebo simulation.

`--headless` A boolean variable providing the ability to run in headless (server-only) mode. This is the [mode of operation in macOS](https://gazebosim.org/docs/harmonic/getstarted#macos), and is more suitable for container use.

Quy ước màu trục tọa độ:
🔴 X axis = RED (Đỏ)
🟢 Y axis = GREEN (Xanh lá)
🔵 Z axis = BLUE (Xanh dương)
Ghi nhớ: RGB = XYZ

Hệ tọa độ Gazebo (Right-handed coordinate system):

        Z (Blue - Xanh dương)
        ↑
        |
        |
        +----→ X (Red - Đỏ)
       /
      /
     ↓
    Y (Green - Xanh lá)
X (Đỏ): Thường hướng về phía trước (forward)
Y (Xanh lá): Thường hướng sang trái (left)
Z (Xanh dương): Thường hướng lên trên (up)

## TF Studio bridge topics (M3-BE-2)

`server.config` loads a fixed set of `gz-sim` system plugins for every
TF Studio session. The `websocket.gzlaunch` bridge has no topic
allow-list and forwards every advertised topic to the browser, so this
list also reflects what the M3-FE-7 overlays + Foxglove panels can see.

Confirmed-emitting topics on a running session (replace `<w>` with the
world name reported by `gz topic -l`):

| Topic                              | Source plugin / system          | Used by                          |
|------------------------------------|---------------------------------|----------------------------------|
| `/world/<w>/stats`                 | gz-sim (built-in)               | Gazebo panel sim time / RTF pill |
| `/world/<w>/clock`                 | gz-sim (built-in)               | ROS 2 `use_sim_time`             |
| `/world/<w>/scene/info`            | SceneBroadcaster                | gzweb scene tree, M3-FE-7        |
| `/world/<w>/scene/deletion`        | SceneBroadcaster                | gzweb scene tree                 |
| `/world/<w>/state`                 | SceneBroadcaster                | gzweb scene tree                 |
| `/world/<w>/pose/info`             | SceneBroadcaster                | Model-root poses                 |
| `/world/<w>/dynamic_pose/info`     | SceneBroadcaster *(with `<publish_link_pose>true</publish_link_pose>`)* | **Per-link** poses for M3-FE-7 coordinate-frame overlays |
| `/world/<w>/joint_state`           | **JointStatePublisher (M3-BE-2)** | Joint-angle labels for M3-FE-7   |
| `/world/<w>/model/<m>/joint_state` | JointStatePublisher (per model) | Per-model joint introspection    |

### `publish_link_pose`

The `SceneBroadcaster` plugin defaults to publishing model-root poses
only in gz-sim 8 — link-level pose entries (e.g. `x500_0/base_link`)
are gated behind the `<publish_link_pose>true</publish_link_pose>`
child element. M3-FE-7 needs link-level poses to render coordinate
frames at each joint origin, so the flag is set unconditionally in
`server.config`. The setting is idempotent: if a future gz-sim release
flips the default to true, leaving the explicit `true` here is still
correct.

### `JointStatePublisher`

`gz-sim-joint-state-publisher-system` (apt package
`libgz-sim8-joint-state-publisher-system` from
`ros-humble-ros-gzharmonic`, see phase1 §3.3) advertises both:

- `/world/<w>/joint_state` — a combined `gz.msgs.Model` message for
  every joint in every model in the world.
- `/world/<w>/model/<model_name>/joint_state` — one message per
  model, useful when only one vehicle's joints are of interest.

No SDF-level configuration is required; loading the system plugin at
world scope is sufficient.

### Verification commands

After restarting a session with the updated `server.config`:

```bash
# 1. Confirm at least one joint topic is advertised.
gz topic -l | grep joint

# 2. Confirm joint state messages are flowing.
gz topic -e -t /world/<w>/joint_state | head -40

# 3. Confirm per-link poses now appear (look for `<model>/<link>`,
#    e.g. `x500_0/base_link`, in the `name:` fields).
gz topic -e -t /world/<w>/dynamic_pose/info | head -60
```

### Contact sensors — deferred to M7

The `gz-sim-contact-system` plugin is already loaded at world scope
(`server.config`), so any `<sensor type="contact">` element declared
in a model SDF would publish a contact topic automatically. **For
Phase 1, no per-model contact sensors are annotated** in this repo's
`models/x500*/model.sdf` files. Rationale:

- M3-FE-7's coordinate-frame overlays do not require contact data.
- Landing-gear contact visualisation is a stretch goal owned by M7
  ("Multi-vehicle + ground-collision polish").
- The x500 / x500_depth / x500_lidar variants share most links but
  differ in sensor layout; annotating them now would couple the
  Phase 1 model bundle to a stretch deliverable that may yet change
  its preferred per-vehicle topology.

When M7 picks this up, the work is purely SDF edits under
`models/x500*/model.sdf` (adding `<sensor type="contact">` blocks to
the landing-gear `<link>` elements). No `server.config` or
`websocket.gzlaunch` change will be needed.