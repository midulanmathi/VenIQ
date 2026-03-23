import type { Project, PromptSuggestion } from "@/types";

const demoWaveform = (n: number) =>
  Array.from({ length: n }, (_, i) => 0.35 + 0.25 * Math.sin(i * 0.4));

export const MOCK_PROJECTS: Project[] = [
  {
    id: "proj-neon-rhapsody",
    title: "Neon Rhapsody",
    songTitle: "Neon Rhapsody",
    genre: "Synthwave",
    bpm: 120,
    key: "Am",
    lastEdited: "2 hours ago",
    status: "draft",
    collaborators: [
      { id: "1", name: "You", avatar: "https://github.com/shadcn.png" },
    ],
    tracks: [
      {
        id: "t1",
        name: "Lead Vocals",
        type: "vocals",
        color: "#818cf8",
        waveform: demoWaveform(48),
      },
      {
        id: "t2",
        name: "Drums",
        type: "drums",
        color: "#38bdf8",
        waveform: demoWaveform(48),
      },
      {
        id: "t3",
        name: "Bass",
        type: "bass",
        color: "#a78bfa",
        waveform: demoWaveform(48),
      },
      {
        id: "t4",
        name: "Pads",
        type: "pad",
        color: "#f472b6",
        waveform: demoWaveform(48),
      },
    ],
    lyrics: [
      { id: "l1", text: "City lights blur in the rear view", startTime: 0, endTime: 4 },
      { id: "l2", text: "Heartbeat syncs with the tempo", startTime: 4, endTime: 8 },
    ],
    versions: [
      {
        id: "v1",
        title: "Original Demo",
        duration: "3:24",
        tags: ["demo", "draft"],
        date: "2026-03-20",
        status: "Original",
      },
    ],
  },
];

export const SUGGESTIONS: PromptSuggestion[] = [
  { id: "s1", text: "Add warm analog pads under the chorus", category: "compose" },
  { id: "s2", text: "Tighten the snare transient at 1:12", category: "edit" },
  { id: "s3", text: "Create a lo-fi remix of the hook", category: "remix" },
  { id: "s4", text: "Rewrite verse 2 with more imagery", category: "lyrics" },
  { id: "s5", text: "Gentle master: -1dB ceiling, widen stereo 10%", category: "master" },
];
