#!/usr/bin/env python3
"""
Generate image prompts for each temple room from the JSON data
These can be used with Stable Diffusion, DALL-E, Midjourney, etc.
"""

import json
import os

def load_temple_data(filepath):
    """Load the temple JSON data"""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_room_prompts(temple_data):
    """Generate optimized image generation prompts for each room"""
    
    # Base style prompt for consistency
    base_style = ("legends of the hidden temple TV show set, nickelodeon 1990s, "
                 "ancient mayan aztec temple room, stone walls with hieroglyphs, "
                 "dramatic torch lighting, mysterious atmosphere, "
                 "game show set design, practical effects, ")
    
    room_prompts = {}
    
    for room_id, room_data in temple_data['rooms'].items():
        room_name = room_data['name']
        description = room_data['description']
        
        # Build specific prompt based on room characteristics
        specific_elements = []
        
        # Add room-specific elements based on keywords
        if 'skeleton' in room_name.lower() or 'crypt' in room_id:
            specific_elements.append("ancient skeletons, bones, skulls on shelves")
        
        if 'throne' in room_name.lower():
            specific_elements.append("golden throne, royal chamber, ornate decorations")
        
        if 'spider' in room_name.lower():
            specific_elements.append("giant spider webs, egg sacs, creepy crawlies")
        
        if 'swamp' in room_name.lower():
            specific_elements.append("murky water, fog, hanging vines, moss")
        
        if 'forest' in room_name.lower():
            specific_elements.append("artificial trees, dark foliage, hidden passages")
        
        if 'silver monkey' in room_name.lower():
            specific_elements.append("pedestal with three piece silver monkey statue puzzle")
        
        if 'pit' in room_name.lower():
            specific_elements.append("deep pit, rope bridges, vertical chamber")
        
        if 'mirror' in room_name.lower():
            specific_elements.append("wall of mirrors, reflections, optical illusions")
        
        if 'crystal' in room_name.lower():
            specific_elements.append("glowing crystals, purple and blue lights, mystical cave")
        
        if 'lightning' in room_name.lower():
            specific_elements.append("tesla coils, electrical effects, metal rods, sparks")
        
        if 'observatory' in room_name.lower():
            specific_elements.append("celestial wheel, planets, stars on ceiling, astronomical devices")
        
        if 'heart' in room_name.lower() and 'temple' in room_name.lower():
            specific_elements.append("sacred altar, jade serpent crown on pedestal, golden light, inner sanctum")
        
        if 'viper' in room_name.lower() or 'snake' in room_name.lower():
            specific_elements.append("ceramic pots, rubber snakes, snake decorations")
        
        if 'waterfall' in room_name.lower():
            specific_elements.append("rushing waterfall, wet rocks, hidden passage behind water")
        
        if 'quicksand' in room_name.lower():
            specific_elements.append("sand pit, sinking hazard, overhead rope")
        
        if 'treasure' in room_name.lower():
            specific_elements.append("gold coins, treasure chests, jewels, ancient artifacts")
        
        if 'gargoyle' in room_name.lower():
            specific_elements.append("three stone gargoyles, grotesque faces, moveable tongues")
        
        if 'jester' in room_name.lower():
            specific_elements.append("court jester paintings, colorful medieval decorations, bells")
        
        if 'music' in room_name.lower():
            specific_elements.append("ancient drums, gongs, bone xylophone, musical instruments")
        
        if 'tomb' in room_name.lower():
            specific_elements.append("sarcophagus, egyptian style decorations, burial chamber")
        
        if 'mine' in room_name.lower():
            specific_elements.append("mining elevator, wooden supports, vertical shaft, chains")
        
        if 'elements' in room_name.lower():
            specific_elements.append("four element symbols, fire water earth air, mystical circles")
        
        # Build the complete prompt
        elements_str = ", ".join(specific_elements) if specific_elements else description
        
        full_prompt = f"{base_style}{elements_str}, {room_name} room"
        
        # Add negative prompt for better quality
        negative_prompt = ("modern, contemporary, bright lighting, clean, text, "
                          "people, contestants, cameras, crew, watermark, "
                          "low quality, blurry, deformed")
        
        # Get the image filename from the room data if it exists
        image_filename = room_data.get('image_file', f'temple_room_{room_id}.png')
        
        room_prompts[room_id] = {
            "room_name": room_name,
            "image_filename": image_filename,
            "positive_prompt": full_prompt,
            "negative_prompt": negative_prompt,
            "short_prompt": f"Legends of Hidden Temple room: {room_name}, {', '.join(specific_elements[:3]) if specific_elements else description[:50]}",
            "settings_suggestion": {
                "steps": 30,
                "cfg_scale": 7.5,
                "size": "768x512",
                "sampler": "DPM++ 2M Karras"
            }
        }
    
    return room_prompts

def save_prompts(room_prompts, output_file):
    """Save prompts to a JSON file"""
    with open(output_file, 'w') as f:
        json.dump(room_prompts, f, indent=2)
    print(f"Saved {len(room_prompts)} room prompts to {output_file}")

def update_temple_with_image_files(temple_file, room_prompts):
    """Update the main temple JSON with image filenames"""
    # Load the temple data
    with open(temple_file, 'r') as f:
        temple_data = json.load(f)
    
    # Update each room with its image filename
    updated_count = 0
    for room_id, room_data in temple_data['rooms'].items():
        if room_id in room_prompts:
            # Add or update the image_file property
            room_data['image_file'] = room_prompts[room_id]['image_filename']
            updated_count += 1
    
    # Save the updated temple data
    with open(temple_file, 'w') as f:
        json.dump(temple_data, f, indent=2)
    
    print(f"Updated {updated_count} rooms in {temple_file} with image filenames")

def display_sample_prompts(room_prompts, num_samples=3):
    """Display a few sample prompts"""
    print("\n" + "="*80)
    print("SAMPLE IMAGE GENERATION PROMPTS")
    print("="*80 + "\n")
    
    sample_rooms = ['entrance', 'crypt', 'heart_chamber']
    
    for room_id in sample_rooms:
        if room_id in room_prompts:
            room = room_prompts[room_id]
            print(f"🏛️  {room['room_name'].upper()}")
            print("-" * 40)
            print(f"Prompt: {room['short_prompt']}")
            print(f"\nFull Prompt (first 200 chars):")
            print(f"{room['positive_prompt'][:200]}...")
            print("\n")

def main():
    """Main execution"""
    temple_file = '/home/aaron/Projects/games/maze/temple-map-graph.json'
    output_file = '/home/aaron/Projects/games/maze/temple-room-prompts.json'
    
    # Load temple data
    temple_data = load_temple_data(temple_file)
    
    # Generate prompts
    room_prompts = create_room_prompts(temple_data)
    
    # Save prompts to file
    save_prompts(room_prompts, output_file)
    
    # Update the main temple JSON with image filenames
    update_temple_with_image_files(temple_file, room_prompts)
    
    # Display samples
    display_sample_prompts(room_prompts)
    
    print(f"\n✨ Ready to generate images for {len(room_prompts)} temple rooms!")
    print("\nThe temple-map-graph.json has been updated with image filenames.")
    print("The game will automatically display images when they exist in room_images/")
    
    print("\n" + "="*60)
    print("🎨 IMAGE GENERATION OPTIONS")
    print("="*60)
    
    print("\n📋 AUTOMATIC GENERATION (Recommended):")
    print("  Use generate_temple_images.py with local Stable Diffusion")
    print("  ")
    print("  Requirements:")
    print("  1. Install Stable Diffusion WebUI (Automatic1111)")
    print("     git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui")
    print("  ")
    print("  2. Start with API enabled on port 7860:")
    print("     ./webui.sh --api --listen")
    print("  ")
    print("  3. Run the batch generator:")
    print("     ./generate_temple_images.py")
    print("  ")
    print("  The generator will:")
    print("  • Connect to SD API at http://localhost:7860")
    print("  • Generate all 24 temple room images")
    print("  • Save to room_images/ directory")
    print("  • Show progress and allow retries")
    
    print("\n🎨 MANUAL GENERATION (Alternative):")
    print("  Use the prompts in temple-room-prompts.json with:")
    print("  • DALL-E 3")
    print("  • Midjourney") 
    print("  • Leonardo AI")
    print("  • Stable Diffusion online")
    print("  ")
    print("  Save images with exact filenames from the JSON")
    print("  Example: temple_room_crypt.png")
    
    print("\n💡 TIPS:")
    print("  • Use negative prompts to avoid modern elements")
    print("  • Recommended size: 768x512 pixels")
    print("  • Best model: Stable Diffusion 1.5")
    print("  • CFG Scale: 7.5, Steps: 30")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
