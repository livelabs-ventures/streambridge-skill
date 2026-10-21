# Play world layer

Every event with a course gets a play world: 3D terrain around the course, built by StreamBridge's server, shown as the map on the event's public page. The **world layer** is what you place in that world: sponsor placements, course points (aid, water, cut-offs, climbs, landmarks) and hotspots. Viewers see changes within seconds, without reloading.

You never build or upload terrain. The server builds a course's world when its GPX is uploaded or imported; you can only ask it to build again.

## Courses and their worlds

```bash
bash scripts/streambridge courses list <event-id>
bash scripts/streambridge courses rebuild-world <event-id> <course-key-or-id>
```

`courses list` shows each course's `route_key`, `distance_km`, `parse_status` and `world_status` (`building`, `ready`, `failed` with `world_error`, or null before a build). A course without a ready world shows satellite instead, and draws no elements.

## The workflow: pull, edit, check, push

```bash
bash scripts/streambridge world pull <event-id> world.json     # the layer as a file
# edit world.json
bash scripts/streambridge world check <event-id> world.json    # validate on the server, saves nothing
bash scripts/streambridge world push <event-id> world.json     # save; viewers update live
```

Push replaces the whole layer: elements with an `id` are updated, elements without one are created, and elements you removed from the file are deleted. The file carries the `version` you pulled. If someone changed the layer since, push answers `409 version_conflict`: pull again, re-apply your edits, push again. Never paste the newer version number into an old file to force it through.

For one change, skip the file:

```bash
bash scripts/streambridge world place <event-id> --kind sponsor --campaign cell_c --course 100_miler --km 0.2
bash scripts/streambridge world place <event-id> --kind point --type water --course 100_miler --km 21.1 --label "Km 21 water"
bash scripts/streambridge world place <event-id> --kind hotspot --action camera --camera <stream-id> --lat -33.95 --lng 18.41 --label "Summit cam"
bash scripts/streambridge world place <event-id> --kind hotspot --action link --url https://example.com/route --course 100_miler --km 42 --label "Route notes" --hidden
bash scripts/streambridge world remove <event-id> <element-id>
```

`--campaign` takes a campaign's id, tag or sponsor name. `--course` takes a course key or id.

## The file

```json
{
  "version": 7,
  "elements": [
    {
      "id": "2f6c…",
      "kind": "sponsor",
      "campaign_id": "9a1e…",
      "campaign_tag": "cell_c",
      "route_id": "51b0…",
      "route_key": "100_miler",
      "km": 0.2,
      "lat": null,
      "lng": null,
      "action": "card",
      "label": null,
      "note": "Official network partner",
      "visible": true
    },
    {
      "kind": "point",
      "point_type": "water",
      "route_key": "100_miler",
      "km": 21.1,
      "label": "Km 21 water",
      "note": "Water and electrolytes"
    }
  ]
}
```

The second element has no `id`, so push creates it. `campaign_tag`, `route_key` (when it agrees with `route_id`), `stream_name`, `position`, `created_at` and `updated_at` are there for you to read; the server ignores them. The order of `elements` is the layer's order.

## Element rules

| Field | Rules |
|---|---|
| `kind` | `sponsor`, `point` or `hotspot` |
| `point_type` | Required for a `point`: `aid`, `water`, `cutoff`, `climb`, `landmark`. Null otherwise |
| Anchor | Either a course and distance (`route_id` or `route_key`, plus `km` between 0 and the course's `distance_km`) or a point (`lat` and `lng`). Never both |
| `action` | What pressing it does: `card` (the default: shows the label and note; a sponsor's card has a Visit button), `camera` (needs `stream_id`, one of the event's cameras; opens it), `link` (needs `url`, https only; opens in a new tab) |
| `campaign_id` | Required for a `sponsor`, not allowed on other kinds. Must be one of the event's campaigns (`sponsors list`) |
| `label` | Up to 40 characters. Required for points and hotspots; a sponsor shows its sponsor name when it has none |
| `note` | Up to 280 characters |
| `look` | `marker` (the default: a pin with a card) or `prop` (a 3D prop, below). Only sponsors take a prop |
| `prop` | With `look: "prop"`: `arch`, `board`, `flag_line`, `inflatable` or `podium` |
| `heading_deg` | For a prop at a point (`lat`/`lng`): the compass direction it faces, 0–359. On a course, a prop faces along it, so leave this out |
| `visible` | `false` keeps the element in the layer but off the public page |

At most 200 elements per event, 24 of them props. Text shows as plain text.

Sponsor artwork always comes from the campaign: the logo is the marker, and the click-through link is the card's Visit button. To change artwork or the link, use `sponsors set`. A paused campaign's placements disappear from the world until it resumes; deleting a campaign, course or camera deletes the elements that depend on it.

Viewers don't see:

- hidden elements;
- a sponsor whose campaign is paused;
- a camera hotspot whose camera is hidden from the public page;
- any element on a course whose world isn't ready.

## 3D sponsor props

A sponsor can stand in the world as a 3D prop from our own library instead of a pin. The campaign's artwork goes on the prop: its mobile banner on a board, its logo on the others. Its marker floats above the prop, and pressing either one opens the sponsor card. Nobody uploads models; these six are the library.

| `prop` | What it is | Where it goes |
|---|---|---|
| `arch` | An inflatable arch over the course | The start (km 0.1) and the finish (a few hundred metres before `distance_km`). Runners pass through it |
| `board` | A billboard beside the course | Climbs, aid stations, landmarks |
| `flag_line` | A row of feather flags along the course | A long straight, or the run-in to the finish |
| `inflatable` | A tall inflatable column | A spot spectators gather at, seen from far off |
| `podium` | 1-2-3 steps | The finish area |
| `airship` | A blocky zeppelin in the sponsor's colour (taken from its logo), with the logo on both sides, circling high over its anchor | Over the whole race: anchor it near the middle of the course. One per event |

```bash
bash scripts/streambridge world place <event-id> --kind sponsor --campaign cell_c --course 42_km --km 0.1 --prop arch
bash scripts/streambridge world place <event-id> --kind sponsor --campaign cell_c --lat -34.048 --lng 18.4236 --prop podium --heading 120
```

Props are landmark-sized: viewers see them when they zoom in or fly the route, and the sponsor's pill marks them from afar. In a file, the element carries `"look": "prop", "prop": "arch"`. Keep props to the moments that matter: at most 24 per event, and well apart. A prop on a course stands beside the line (an arch straddles it) and faces along it.

## Placing things well

- **Anchor to the course** (`route_key` + `km`) whenever the thing is on the course. A km anchor sits on the line and survives a corrected GPX; a lat/lng point doesn't follow the course.
- **Sponsors:** the title sponsor at the start (km 0.1–0.3) and finish (a few hundred metres before `distance_km`), as arches. Others at aid stations, climbs or landmarks they're tied to, at least 2 km apart, as boards or markers. One sponsor per spot.
- **Course points:** use the race's official aid, water and cut-off kilometres. Labels short and scannable: "Km 42 aid", "Cut-off 14:00", "Chapman's Peak".
- **Hotspots:** a camera hotspot where a camera actually stands; a link only to a page that helps a spectator (route notes, results).
- **Before a race, stage with `visible: false`,** check, then flip to true.
- **Check before you push,** and fix every `elements[n].field` error the server lists.

## Seeing it

Open the event's public page and its map: the world shows each element on its course. A placement on a course whose world is still building shows once the world is ready.

## API and MCP

REST, all under `/api/v1`:

- `GET /events/:event_id/world` reads the layer.
- `PUT /events/:event_id/world` replaces it: `{version, elements}`, with `?dry_run=true` to check.
- `POST /events/:event_id/world/elements` adds one element.
- `PATCH /events/:event_id/world/elements/:id` and `DELETE /events/:event_id/world/elements/:id` change or delete one.
- `POST /events/:event_id/routes/:id/world/rebuild` builds a course's world again.
- `GET /public/events/:event_id/world` is the public layer.

The general MCP profile (`/mcp`) has `get_event_world`, `place_world_element`, `update_world_element`, `remove_world_element` and `rebuild_course_world`.
