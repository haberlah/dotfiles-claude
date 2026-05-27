# Codex rollout JSONL format

Read this before hand-editing a rollout. It explains the record types, which
records the model actually replays, and where the bloat lives. Grounded in the
open-source `codex-rs` core (the Rust process that writes and loads rollouts).

## File location and shape

`~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl`

One JSON object per line. The filename `<uuid>` matches the `id` inside the
first `session_meta` record. The loader reads line by line and **skips
unparseable lines non-fatally** (it logs and continues) - but don't rely on
that; always emit valid JSON.

## Record types (`RolloutItem`)

Each line has a `type` and (usually) a `payload`:

| `type`         | Purpose | Fed to the model on resume? |
| -------------- | ------- | --------------------------- |
| `session_meta` | Header: `id`, `timestamp`, `cwd`, `originator`, `cli_version`, `base_instructions`. **Mandatory** - the first one with an `id` defines the thread. | n/a (required to load) |
| `response_item`| The conversation items the model sees. | **Yes** |
| `compacted`    | A `/compact` checkpoint: `{message, replacement_history}`. The **newest** one supersedes everything older on resume. | The newest one: **yes** |
| `turn_context` | Per-turn settings (model, effort, cwd, instructions). | Indirectly |
| `event_msg`    | UI/telemetry event stream (e.g. `mcp_tool_call_end`, `user_message`, `token_count`, `task_started`/`task_complete`). | **No - display only** |

### `response_item` payload variants

`message` (with `role` user/assistant and a `content` array), `reasoning`,
`function_call` (has a `call_id`), `function_call_output` (references a
`call_id`), plus tool variants (`custom_tool_call(_output)`,
`local_shell_call`, `tool_search_call`/`_output`, `web_search_call`).

## What is replayed vs display-only (the key lever)

On resume Codex rebuilds the model input from **`response_item`s plus the active
(newest) `compacted.replacement_history`**. `event_msg` records are **not** sent
to the model - they drive the transcript UI and telemetry only.

So **display-only bloat can be removed with zero model-context loss**, and is the
first thing to attack. In practice the same screenshots are stored in *both*
places, so stripping images covers both at once.

## Where the bloat lives

Screenshots from the `computer-use` / browser tool, stored two ways:

1. **Model-facing** - inside `response_item` `function_call_output` (and
   sometimes `message`) `content` arrays as
   `{"type":"input_image","image_url":"data:image/...;base64,...","detail":"high"}`,
   and copied into `compacted.replacement_history`.
2. **Display-only** - inside `event_msg` `mcp_tool_call_end` results as MCP
   blocks `{"type":"image","data":"<base64>","mimeType":"image/jpeg"}` (note: no
   `data:` prefix), and as bare `data:image` strings in `user_message.images[]`.

Text (messages, reasoning, function call args, tool-output text) is usually a
small fraction of the file. On one real 1.27 GB session, ~56% was base64 images
and another large slice was redundant older `compacted` checkpoints; the actual
conversation text was a few tens of MB.

## Resume semantics (why slimming changes context)

Codex resumes by **stateless replay**: it sends the full reconstructed input to
the model each turn (`store=false`, no `previous_response_id`). The local rollout
*is* the model's memory. Therefore:

- Removing display-only `event_msg` content and superseded `compacted` records
  changes nothing the model sees.
- Removing images / truncating outputs / cutting turns *does* reduce model
  context - acceptable for continuation, but apply least-lossy first.

## Integrity rules enforced on load / replay

- **`session_meta` id required.** No id anywhere -> loader errors "failed to
  parse thread ID".
- **Tool-call pairing self-heals.** `normalize_history` (release builds)
  synthesises an "aborted" output for an orphaned `function_call` and drops an
  orphaned `function_call_output`. So a cut that splits a pair is tolerated.
- **Reasoning items do not self-heal.** A leading orphaned `reasoning` item (with
  `encrypted_content`) is rejected by the Responses API. Cut only on a
  **user-message boundary** so the first retained item is a user message.
- **Replayed images are validated.** Any image in the replayed history must be a
  valid, adequately-sized image. A 1x1 placeholder is rejected ("Invalid image in
  your last message"). Replace images with **text**.

## Size ceiling

The desktop app aggregates the whole rollout into one string; Node/V8 caps a
string at **536,870,888 bytes**. The repair targets ~400 MB by default for
margin. The number that actually governs the crash is the aggregate string size,
which tracks file size closely, so keeping the file well under the ceiling is
sufficient.
