# Legends of the Hidden Temple - Temple Run Simulator

## Project Overview
An interactive terminal-based recreation of the classic 90s Nickelodeon game show "Legends of the Hidden Temple". Players navigate through a 24-room temple maze, avoiding Temple Guards, racing against time, and searching for the legendary Jade Serpent's Crown.

## Features
- 🏛️ **24 Interconnected Temple Rooms**: Complex branching paths with multiple routes to victory
- ⏱️ **3-Minute Timer**: Race against time like the original show
- 💂 **Temple Guards**: Randomly placed guards that cost Pendants of Life
- 🏆 **Authentic Prize System**: Win 90s prizes including trips to Space Camp!
- 🎨 **AI-Generated Room Images**: Display room visuals using chafa in terminal
- 🎭 **Olmec Narration**: Dramatic storytelling in the style of the show
- 📊 **Dynamic Pathfinding**: Multiple solutions through the temple maze

## Project Structure
```
/home/aaron/Projects/games/maze/
├── temple-map-graph.json          # Main temple structure with 24 rooms & image refs
├── temple-prizes.json             # 90s-authentic prize database
├── temple-room-prompts.json       # AI image generation prompts
├── temple_runner.py               # Main game engine with chafa image display
├── generate_room_prompts.py       # Creates prompts & updates temple JSON
├── generate_temple_images.py      # Batch image generator via SD API
└── room_images/                   # Generated room images (768x512)
    ├── temple_room_entrance.png
    ├── temple_room_crypt.png
    └── ... (24 room images total)
```

## Quick Start

### Play the Game
```bash
python3 temple_runner.py
```

### Generate Room Images

1. **Generate/Update prompts and filenames**:
   ```bash
   python3 generate_room_prompts.py
   # This updates temple-map-graph.json with image filenames automatically
   ```

2. **Generate images with local Stable Diffusion**:
   ```bash
   # Make sure SD WebUI is running with --api flag
   python3 generate_temple_images.py
   # Select option 2 to generate missing rooms only
   ```

3. **Or manually create with other tools**:
   - Use prompts from `temple-room-prompts.json`
   - Save with exact filenames specified (e.g., `temple_room_crypt.png`)
   - Place in `room_images/` directory

## Technical Components

### Core Game Engine (`temple_runner.py`)
- **TempleRunner**: Main game loop with time management
- **Player**: Tracks pendants, path, artifact status
- **PrizeTracker**: Awards authentic 90s prizes based on performance
- **Image Display**: Uses chafa for terminal image rendering

### Temple Structure (`temple-map-graph.json`)
- 24 rooms with unique descriptions and challenges
- Multiple interconnected paths (3-4 connections per room)
- Special rooms: Heart Chamber (artifact), Temple Guard locations
- Each room has `image_file` property for visual display

### Prize System (`temple-prizes.json`)
- Participation prizes: Nickelodeon T-shirts, Nestle Crunch
- Round prizes: Moon Shoes, Pogs, British Knights sneakers
- Temple Games: Huffy bikes, Sega Game Gear
- Grand Prize: Trip to Space Camp ($2000 value!)
- Bonus achievements: Speed runs, perfect runs

### Image Generation System
- **Prompts**: Optimized for "90s TV game show set" aesthetic
- **Style**: Ancient Mayan/Aztec temple with dramatic torch lighting
- **Negative prompts**: Excludes modern elements, people, text
- **Integration**: Automatic display when entering rooms

## Room Navigation Map
```
ENTRANCE → CRYPT → PIT OF DESPAIR → THRONE ROOM
    ↓         ↓           ↓              ↓
SPIDER LAIR  OBSERVATORY  MINE SHAFT   SWAMP
    ↓         ↓           ↓              ↓
[Multiple interconnected paths leading to...]
              HEART CHAMBER (Crown Location)
```

## Game Mechanics

### Winning Conditions
1. Find the Jade Serpent's Crown in the Heart Chamber
2. Return to the Entrance
3. Complete within 3 minutes
4. Don't lose all Pendants of Life

### Temple Guards
- 3 guards randomly placed in valid rooms
- Cost 1 Pendant of Life to pass
- Start with 2 Pendants
- Getting caught with 0 Pendants = Game Over

### Scoring & Prizes
- Rooms explored affects prize tier
- Speed bonus for completion under 60 seconds
- Perfect run bonus for avoiding all guards
- 100% exploration bonus for visiting all 24 rooms

## Development Notes

### Image Display Requirements
- Install chafa for terminal image display: `sudo apt install chafa`
- Images display at 60x30 character size
- Fallback to text-only if chafa unavailable

### Extending the Game
- Add new rooms: Update `temple-map-graph.json`
- Add prizes: Update `temple-prizes.json`
- Modify difficulty: Adjust timer, guards, pendant count
- Custom legends: Create new artifact stories

## AI Image Generation Tips

### Recommended Prompt Structure
```
Positive: "legends of the hidden temple TV show set, nickelodeon 1990s, 
          ancient mayan aztec temple room, stone walls with hieroglyphs, 
          dramatic torch lighting, [ROOM SPECIFIC ELEMENTS]"

Negative: "modern, contemporary, bright lighting, clean, text, people, 
          contestants, cameras, crew, watermark"
```

### Best Models/Settings
- Stable Diffusion 1.5 or SDXL
- Steps: 30-40
- CFG Scale: 7-8
- Sampler: DPM++ 2M Karras
- Size: 768x512 (or 512x768 for vertical rooms)

## Troubleshooting

### No Images Displaying
- Check chafa is installed: `which chafa`
- Verify images exist in `room_images/`
- Ensure image filenames match JSON: `temple_room_[room_id].png`

### Game Performance
- Reduce image size to 60x30 in display_room_image()
- Disable images: Set `self.enable_images = False`
- Adjust time.sleep() delays for faster gameplay

## Future Enhancements
- [ ] Multiplayer racing mode
- [ ] Team selection (Red Jaguars, Blue Barracudas, etc.)
- [ ] Moat Crossing mini-game
- [ ] Steps of Knowledge trivia
- [ ] Temple Games challenges
- [ ] Leaderboard system
- [ ] Custom temple layouts
- [ ] Voice synthesis for Olmec

## Credits
Based on "Legends of the Hidden Temple" © Nickelodeon/Viacom
Created as an educational project and tribute to 90s game shows.

## Quick Commands Reference
```bash
# Run the game
python3 temple_runner.py

# Generate AI prompts
python3 generate_room_prompts.py

# Create test images
python3 generate_temple_images.py

# Update JSON with image files
python3 add_image_filenames.py

# View temple structure
cat temple-map-graph.json | jq '.rooms | keys'

# Check installed prizes
cat temple-prizes.json | jq '.prizes.temple_run.temple_completion.grand_prizes[0].name'
```

---
*The choices are yours and yours alone. Good luck!* - Olmec