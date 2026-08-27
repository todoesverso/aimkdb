# How to Create a Simple LV2 Audio Plugin in C on Linux

**Category:** Programming
**Subcategory:** Audio
**Tags:** C, audio plugin, LV2, JACK, linux, DSP, DISTRHO, jalv
**Type:** tutorial



## 1. Goal

We are going to build the smallest useful LV2 plugin: a **gain plugin**.

It will take audio:

```text
input ──> [ Gain × ] ──> output
```

and multiply every audio sample by a gain value:

$$
y[n] = g \cdot x[n]
$$

For example:

```text
gain = 0.5

input:   0.8  0.4 -0.6
output:  0.4  0.2 -0.3
```

We'll implement it in **C**, build it as a shared library, install the LV2 bundle, and test it using **Jalv** on Linux.

---

# 2. What Is LV2?

LV2 is a plugin standard for Linux and other Unix-like systems.

An LV2 plugin consists of two major pieces:

```text
LV2 Plugin
│
├── Binary code
│   └── plugin.so
│
└── Metadata
    └── *.ttl
```

The C code implements the DSP.

The `.ttl` files describe the plugin to LV2 hosts.

So unlike simply writing:

```text
myplugin.so
```

you normally create an LV2 **bundle**:

```text
mygain.lv2/
├── manifest.ttl
├── mygain.ttl
└── mygain.so
```

---

# 3. Architecture

The host is responsible for the plugin lifecycle.

```text
                     LV2 Host
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      instantiate     connect      run
          │            │            │
          ▼            ▼            ▼
       plugin       ports        DSP loop
                                    │
                                    ▼
                              process samples
```

Your plugin should **not** create its own audio thread.

The host provides the audio buffers and calls your plugin's `run()` function.

Conceptually:

```text
Host
 │
 │ input buffer
 │ output buffer
 ▼
plugin->run()
 │
 │
 └── for each sample:
       output[i] = input[i] * gain
```

---

# 4. Install the LV2 Development Files

On Debian/Ubuntu:

```bash
sudo apt install lv2-dev
```

For testing:

```bash
sudo apt install jalv
```

You can check that LV2 is installed:

```bash
lv2ls
```

You should see a list of installed LV2 plugins.

Check Jalv:

```bash
jalv --version
```

---

# 5. Create the Project

Let's create:

```text
mygain/
├── Makefile
├── mygain.c
└── mygain.lv2/
    ├── manifest.ttl
    └── mygain.ttl
```

Create it:

```bash
mkdir -p mygain/mygain.lv2
cd mygain
```

---

# 6. The C Plugin

Create:

```text
mygain.c
```

with:

```c
#include <lv2/core/lv2.h>

#include <stdint.h>
#include <stdlib.h>

#define MYGAIN_URI "http://example.org/plugins/mygain"

typedef struct {
    const float *input;
    float *output;
    const float *gain;
} MyGain;

static LV2_Handle
instantiate(const LV2_Descriptor *descriptor,
            double sample_rate,
            const char *bundle_path,
            const LV2_Feature *const *features)
{
    (void)descriptor;
    (void)sample_rate;
    (void)bundle_path;
    (void)features;

    return calloc(1, sizeof(MyGain));
}
```

So far we're only allocating the plugin's state.

---

# 7. Connect the Ports

LV2 plugins expose **ports**.

Our plugin has three:

```text
Port 0: input audio
Port 1: output audio
Port 2: gain control
```

Add:

```c
static void
connect_port(LV2_Handle instance,
             uint32_t port,
             void *data)
{
    MyGain *plugin = (MyGain *)instance;

    switch (port) {
    case 0:
        plugin->input = (const float *)data;
        break;

    case 1:
        plugin->output = (float *)data;
        break;

    case 2:
        plugin->gain = (const float *)data;
        break;
    }
}
```

The host calls this function to tell us where each port's data lives.

---

# 8. The DSP Function

Now comes the interesting part.

```c
static void
run(LV2_Handle instance, uint32_t n_samples)
{
    MyGain *plugin = (MyGain *)instance;

    const float gain = *plugin->gain;

    for (uint32_t i = 0; i < n_samples; ++i) {
        plugin->output[i] = plugin->input[i] * gain;
    }
}
```

This is the entire DSP algorithm:

$$
y[n] = x[n]g
$$

For example:

```text
input:

 0.2
 0.4
-0.8
 0.5


gain = 0.5


output:

 0.1
 0.2
-0.4
 0.25
```

---

# 9. Cleanup

When the host is finished with the plugin:

```c
static void
cleanup(LV2_Handle instance)
{
    free(instance);
}
```

---

# 10. The Complete C File

Put everything together:

```c
#include <lv2/core/lv2.h>

#include <stdint.h>
#include <stdlib.h>

#define MYGAIN_URI "http://example.org/plugins/mygain"

typedef struct {
    const float *input;
    float *output;
    const float *gain;
} MyGain;

static LV2_Handle
instantiate(const LV2_Descriptor *descriptor,
            double sample_rate,
            const char *bundle_path,
            const LV2_Feature *const *features)
{
    (void)descriptor;
    (void)sample_rate;
    (void)bundle_path;
    (void)features;

    return calloc(1, sizeof(MyGain));
}

static void
connect_port(LV2_Handle instance,
             uint32_t port,
             void *data)
{
    MyGain *plugin = (MyGain *)instance;

    switch (port) {
    case 0:
        plugin->input = (const float *)data;
        break;

    case 1:
        plugin->output = (float *)data;
        break;

    case 2:
        plugin->gain = (const float *)data;
        break;
    }
}

static void
run(LV2_Handle instance, uint32_t n_samples)
{
    MyGain *plugin = (MyGain *)instance;

    const float gain = *plugin->gain;

    for (uint32_t i = 0; i < n_samples; ++i) {
        plugin->output[i] = plugin->input[i] * gain;
    }
}

static void
cleanup(LV2_Handle instance)
{
    free(instance);
}

static const LV2_Descriptor descriptor = {
    MYGAIN_URI,
    instantiate,
    connect_port,
    NULL,
    run,
    NULL,
    cleanup,
    NULL
};

LV2_SYMBOL_EXPORT
const LV2_Descriptor *
lv2_descriptor(uint32_t index)
{
    if (index == 0) {
        return &descriptor;
    }

    return NULL;
}
```

There are eight descriptor callbacks/fields here, but our simple plugin only needs:

```text
instantiate
connect_port
run
cleanup
```

---

# 11. LV2 Metadata

The C library isn't enough.

The host needs to know:

```text
What is this plugin?
What ports does it have?
Which ports are audio?
Which are inputs?
Which are outputs?
What is the default gain?
What range does gain have?
```

That's what Turtle (`.ttl`) metadata provides.

---

# 12. `manifest.ttl`

Create:

```text
mygain.lv2/manifest.ttl
```

```turtle
@prefix lv2: <http://lv2plug.in/ns/lv2core#> .

<http://example.org/plugins/mygain>
    a lv2:Plugin ;
    lv2:binary <mygain.so> ;
    rdfs:seeAlso <mygain.ttl> .
```

We also need `rdfs`, so the complete file should be:

```turtle
@prefix lv2: <http://lv2plug.in/ns/lv2core#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/plugins/mygain>
    a lv2:Plugin ;
    lv2:binary <mygain.so> ;
    rdfs:seeAlso <mygain.ttl> .
```

---

# 13. `mygain.ttl`

Create:

```text
mygain.lv2/mygain.ttl
```

```turtle
@prefix lv2: <http://lv2plug.in/ns/lv2core#> .
@prefix doap: <http://usefulinc.com/ns/doap#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/plugins/mygain>
    a lv2:Plugin ;
    doap:name "My Gain" ;
    doap:license <http://opensource.org/licenses/isc> ;

    lv2:port [
        a lv2:AudioPort ,
          lv2:InputPort ;

        lv2:index 0 ;
        lv2:symbol "input" ;
        lv2:name "Input"
    ] ;

    lv2:port [
        a lv2:AudioPort ,
          lv2:OutputPort ;

        lv2:index 1 ;
        lv2:symbol "output" ;
        lv2:name "Output"
    ] ;

    lv2:port [
        a lv2:ControlPort ,
          lv2:InputPort ;

        lv2:index 2 ;
        lv2:symbol "gain" ;
        lv2:name "Gain" ;

        lv2:default 1.0 ;
        lv2:minimum 0.0 ;
        lv2:maximum 2.0 ;
    ] .
```

The metadata establishes:

```text
                My Gain
                   |
        +----------+----------+
        |          |          |
      input      output      gain
       audio      audio     control
```

---

# 14. Build the Plugin

Compile the C code as a shared library:

```bash
gcc -fPIC -shared \
    -Wall -Wextra \
    -I/usr/include/lv2 \
    mygain.c \
    -o mygain.lv2/mygain.so
```

Depending on your distribution, the LV2 headers may be found differently. A more portable approach is:

```bash
pkg-config --cflags lv2
```

and:

```bash
pkg-config --libs lv2
```

Then:

```bash
gcc -fPIC -shared \
    -Wall -Wextra \
    $(pkg-config --cflags lv2) \
    mygain.c \
    -o mygain.lv2/mygain.so
```

---

# 15. Install the LV2 Bundle

LV2 looks for plugins in standard directories.

For a user-local installation:

```bash
mkdir -p ~/.lv2
cp -r mygain.lv2 ~/.lv2/
```

You can then inspect the plugin:

```bash
lv2ls | grep mygain
```

You should see:

```text
http://example.org/plugins/mygain
```

You can also use:

```bash
lv2info http://example.org/plugins/mygain
```

This is an excellent debugging tool because it lets you verify that LV2 understands your metadata.

---

# 16. Test With Jalv

Jalv is a small LV2 host designed specifically for testing plugins.

Run:

```bash
jalv -n mygain http://example.org/plugins/mygain
```

Depending on your audio backend/system, Jalv may connect through JACK or another supported backend.

The plugin should start and expose:

```text
input
output
gain
```

---

# 17. Connect It to Audio

On a JACK/PipeWire system, you can inspect ports using:

```bash
pw-link -l
```

or:

```bash
jack_lsp
```

depending on your setup.

You should eventually have something conceptually like:

```text
Audio source
     |
     v
  mygain:input
     |
   [ × gain ]
     |
     v
  mygain:output
     |
     v
Audio sink
```

With PipeWire, `pw-link` is often the most convenient way to inspect and connect ports.

---

# 18. Try Different Gain Values

The control port is:

```text
gain
```

Jalv provides ways to manipulate control ports depending on the backend/UI being used.

For a simple test, you can start with:

```text
gain = 1.0
```

which gives:

```text
output = input
```

Then:

```text
gain = 0.5
```

gives:

```text
output = input × 0.5
```

And:

```text
gain = 2.0
```

gives:

```text
output = input × 2
```

Be careful with large gains because they can cause clipping.

---

# 19. What's Actually Happening?

This is the most important part.

When you start Jalv:

```text
jalv
  |
  v
LV2 host
```

The host loads:

```text
mygain.so
```

and obtains:

```c
lv2_descriptor(0)
```

The descriptor tells the host:

```text
Plugin URI
instantiate()
connect_port()
run()
cleanup()
```

Then approximately:

```text
Host
 │
 │ instantiate()
 ▼
Plugin instance
 │
 │ connect_port(0, input)
 │ connect_port(1, output)
 │ connect_port(2, gain)
 ▼
Ports connected
 │
 │ run(256)
 ▼
DSP processing
 │
 │ run(256)
 ▼
DSP processing
 │
 │ ...
 ▼
cleanup()
```

---

# 20. The Real-Time DSP Loop

The heart of an audio plugin is essentially:

```c
for (uint32_t i = 0; i < n_samples; ++i) {
    output[i] = input[i] * gain;
}
```

If the host gives you:

```text
n_samples = 256
```

then your plugin processes:

```text
input[0] ... input[255]
```

and produces:

```text
output[0] ... output[255]
```

The next invocation processes the next block.

```text
Audio stream:

──────────────────────────────────────>

       block 1       block 2       block 3
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ 256 samp │  │ 256 samp │  │ 256 samp │
    └──────────┘  └──────────┘  └──────────┘
          │              │              │
          ▼              ▼              ▼
        run()          run()          run()
```

---

# 21. Important Real-Time Rule

Inside `run()`, **do not do things that can block or allocate memory**.

Avoid:

```c
malloc()
free()
printf()
fopen()
sleep()
mutex locking
```

The audio thread needs predictable execution.

Your DSP function should ideally be:

```text
fast
deterministic
non-blocking
allocation-free
```

For example:

```c
static void
run(LV2_Handle instance, uint32_t n_samples)
{
    MyGain *plugin = instance;
    const float gain = *plugin->gain;

    for (uint32_t i = 0; i < n_samples; ++i) {
        plugin->output[i] = plugin->input[i] * gain;
    }
}
```

That's exactly the sort of code we want.

---

# 22. Where the Sample Rate Comes In

Notice that:

```c
instantiate(...)
```

receives:

```c
double sample_rate
```

For example:

```text
44100 Hz
48000 Hz
96000 Hz
```

A gain plugin doesn't care about sample rate.

But a delay does.

For example, if you want a 100 ms delay:

```text
48,000 samples/sec
×
0.1 sec
=
4,800 samples
```

At 96 kHz:

```text
96,000 × 0.1 = 9,600 samples
```

This is why plugins that implement filters, delays, oscillators, etc. generally need to store the sample rate.

---

# 23. A More Interesting Next Plugin: Low-Pass Filter

Once the gain plugin works, the next logical step is a simple one-pole low-pass filter.

The equation can be:

$$
y[n]=(1-\alpha)x[n]+\alpha y[n-1]
$$

Conceptually:

```text
             +----------------+
             |                |
             |       α        |
             |       ×        |
             |       ^        |
             |       |        |
x[n] ───────>+───────+───────> y[n]
             |       |
             |    1-α|
             |       ×
             |       ^
             |       |
             +-------+
```

Now you have:

```text
input
  │
  ▼
filter
  │
  ▼
output
```

and the plugin needs persistent state:

```c
typedef struct {
    const float *input;
    float *output;
    const float *cutoff;

    float state;
    double sample_rate;
} LowPass;
```

This is where DSP and LV2 programming start becoming much more interesting.

---

# 24. The LV2 Programming Model

The most useful abstraction to remember is:

```text
                    LV2 HOST
                       |
                       |
                +------+------+
                |             |
             controls       audio
                |             |
                v             v
             LV2 ports
                |
                v
          +-------------+
          |   Plugin    |
          |             |
          | instantiate |
          | connect     |
          | run         |
          | cleanup     |
          +-------------+
```

Your plugin generally shouldn't know:

```text
Is the host Ardour?
Is it Carla?
Is it Jalv?
Is it a PipeWire application?
Is it another LV2 host?
```

The LV2 API abstracts that away.

---

# 25. LV2 vs JACK vs PipeWire

These technologies are easy to confuse.

They operate at different levels:

```text
             LV2
       Plugin specification
              │
              ▼
            Host
              │
              ▼
        JACK / PipeWire
       Audio infrastructure
              │
              ▼
         Linux kernel
```

Very roughly:

### LV2

Defines how plugins are implemented and described.

### JACK

Provides low-latency audio/MIDI graph infrastructure.

### PipeWire

Modern Linux multimedia infrastructure that can provide JACK compatibility and manage audio/video graphs.

### Jalv

A small LV2 host useful for testing LV2 plugins.

---

# 26. The Minimal Project

Once everything works, your project is remarkably small:

```text
mygain/
│
├── mygain.c
│
└── mygain.lv2/
    ├── manifest.ttl
    ├── mygain.ttl
    └── mygain.so
```

The important relationship is:

```text
mygain.ttl
     │
     │ describes
     ▼
mygain.so
     │
     │ implements
     ▼
DSP
```

---

# 27. Recommended Learning Path

Since you want to learn DSP and implement it in C/Linux, I'd build the plugins in this order:

```text
01. Gain
      │
      ▼
02. Volume / mute
      │
      ▼
03. DC blocker
      │
      ▼
04. One-pole low-pass
      │
      ▼
05. One-pole high-pass
      │
      ▼
06. Delay
      │
      ▼
07. Echo
      │
      ▼
08. Tremolo
      │
      ▼
09. Waveshaper
      │
      ▼
10. Oscillator
      │
      ▼
11. ADSR envelope
      │
      ▼
12. Biquad filter
      │
      ▼
13. Compressor
      │
      ▼
14. FFT analyzer
      │
      ▼
15. Reverb
```

That sequence teaches both sides of the problem:

```text
C/Linux/LV2
     +
DSP mathematics
```

without jumping immediately into a huge framework.

---

# 28. The Big Picture

Ultimately, the thing you're building is:

```text
                         Linux
                           │
                    PipeWire / JACK
                           │
                         Host
                           │
                          LV2
                           │
             ┌─────────────┴─────────────┐
             │                           │
          Metadata                     C code
           (.ttl)                     (.so)
             │                           │
             │                           │
             └─────────────┬─────────────┘
                           │
                        Plugin
                           │
                    ┌──────┴──────┐
                    │             │
                 input           output
                    │             │
                    └─── DSP ─────┘
```

And the DSP itself is ultimately just mathematics implemented as code:

$$
x[n] \rightarrow \boxed{\text{algorithm}} \rightarrow y[n]
$$

For the first plugin:

$$
y[n]=gx[n]
$$

Once you understand this **host → ports → buffers → `run()` → DSP → output** model, you have the foundation for building much more sophisticated LV2 plugins.

