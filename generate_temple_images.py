#!/usr/bin/env python3
"""
Temple Room Image Generator for Legends of the Hidden Temple
Uses Stable Diffusion WebUI API (Automatic1111) at http://localhost:7860
"""

import json
import os
from pathlib import Path
import requests
import base64
import time
from typing import Dict, Any, Optional
import sys

def load_prompts(prompt_file: str) -> Dict:
    """Load room prompts from JSON"""
    with open(prompt_file, 'r') as f:
        return json.load(f)

def ensure_output_dir() -> Path:
    """Create output directory if it doesn't exist"""
    output_dir = Path('/home/aaron/Projects/games/maze/room_images')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def check_api_status(api_url: str = "http://localhost:7860") -> bool:
    """Check if the Stable Diffusion API is running"""
    try:
        response = requests.get(f"{api_url}/sdapi/v1/options", timeout=5)
        if response.status_code == 200:
            print(f"✅ API is running at {api_url}")
            return True
    except:
        pass
    print(f"❌ API not accessible at {api_url}")
    print("   Make sure Automatic1111 WebUI is running with --api flag")
    print("   Launch command: python launch.py --api")
    return False

def get_api_info(api_url: str = "http://localhost:7860") -> Dict:
    """Get information about the API and current settings"""
    info = {}
    try:
        # Get current options
        response = requests.get(f"{api_url}/sdapi/v1/options")
        if response.status_code == 200:
            options = response.json()
            info['model'] = options.get("sd_model_checkpoint", "Unknown")
            
        # Get available samplers
        response = requests.get(f"{api_url}/sdapi/v1/samplers")
        if response.status_code == 200:
            samplers = response.json()
            info['samplers'] = [s['name'] for s in samplers]
            
    except Exception as e:
        print(f"Warning: Could not get API info: {e}")
    
    return info

def ensure_correct_model(api_url: str = "http://localhost:7860") -> bool:
    """Ensure the correct SD 1.5 model is loaded"""
    try:
        # Get current options
        opt = requests.get(url=f'{api_url}/sdapi/v1/options')
        if opt.status_code != 200:
            print(f"❌ Failed to get options: {opt.status_code}")
            return False
            
        opt_json = opt.json()
        current_model = opt_json.get('sd_model_checkpoint', '')
        
        # Check if we need to switch models
        if 'hunyuan' in current_model.lower():
            print("⚠️  Hunyuan model detected, switching to SD 1.5...")
            # Update the model in options
            opt_json['sd_model_checkpoint'] = 'v1-5-pruned-emaonly-fp16.safetensors [e9476a1372]'
            
            # Post the updated options
            response = requests.post(url=f'{api_url}/sdapi/v1/options', json=opt_json)
            if response.status_code == 200:
                print("✅ Switched to SD 1.5 model")
                time.sleep(2)  # Give it a moment to switch models
                return True
            else:
                print(f"❌ Failed to switch model: {response.status_code}")
                return False
                
        elif 'v1-5' in current_model.lower():
            print("✅ SD 1.5 model already active")
            return True
        else:
            print(f"⚠️  Unknown model active: {current_model}")
            print("   Attempting to set SD 1.5 model...")
            opt_json['sd_model_checkpoint'] = 'v1-5-pruned-emaonly-fp16.safetensors [e9476a1372]'
            response = requests.post(url=f'{api_url}/sdapi/v1/options', json=opt_json)
            if response.status_code == 200:
                print("✅ Set to SD 1.5 model")
                time.sleep(2)
                return True
            return False
            
    except Exception as e:
        print(f"❌ Error checking/setting model: {e}")
        return False

def generate_image(room_data: Dict, output_file: Path, api_url: str = "http://localhost:7860",
                  custom_settings: Optional[Dict] = None) -> bool:
    """Generate a single image using the API"""
    
    # Base payload from room data
    payload = {
        "prompt": room_data['positive_prompt'],
        "negative_prompt": room_data['negative_prompt'],
        "steps": room_data['settings_suggestion']['steps'],
        "cfg_scale": room_data['settings_suggestion']['cfg_scale'],
        "width": 768,
        "height": 512,
        "sampler_name": "DPM++ 2M Karras",
        "batch_size": 1,
        "n_iter": 1,
        "seed": -1,  # Random seed
        "subseed": -1,
        "subseed_strength": 0,
        "restore_faces": False,
        "tiling": False,
        "do_not_save_samples": True,
        "do_not_save_grid": True,
    }
    
    # Apply custom settings if provided
    if custom_settings:
        payload.update(custom_settings)
    
    try:
        # Make the API request
        response = requests.post(
            f"{api_url}/sdapi/v1/txt2img",
            json=payload,
            timeout=120  # 2 minutes timeout for generation
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # The API returns base64 encoded images
            if 'images' in result and len(result['images']) > 0:
                image_data = result['images'][0]
                
                # Decode and save the image
                image_bytes = base64.b64decode(image_data)
                with open(output_file, 'wb') as f:
                    f.write(image_bytes)
                
                # Extract seed if available
                seed = "Unknown"
                if 'info' in result:
                    try:
                        info = json.loads(result['info'])
                        seed = info.get('seed', 'Unknown')
                    except:
                        pass
                
                print(f"   ✅ Saved! (seed: {seed})")
                return True
            else:
                print(f"   ❌ No image in response")
                return False
        else:
            print(f"   ❌ API error: {response.status_code}")
            if response.text:
                print(f"      {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Request timed out (120s)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def batch_generate(prompt_data: Dict, output_dir: Path, api_url: str = "http://localhost:7860",
                  skip_existing: bool = True, custom_settings: Optional[Dict] = None) -> None:
    """Generate all temple room images"""
    
    if not check_api_status(api_url):
        return
    
    # Ensure correct model is loaded
    if not ensure_correct_model(api_url):
        print("⚠️  Warning: Could not verify/set model, continuing anyway...")
        print()
    
    # Get API info
    api_info = get_api_info(api_url)
    if api_info.get('model'):
        print(f"📦 Model: {api_info['model']}")
    print(f"📂 Output: {output_dir}")
    print()
    
    total_rooms = len(prompt_data)
    generated = 0
    skipped = 0
    failed = 0
    
    print("Starting generation...")
    print("=" * 60)
    
    for idx, (room_id, room_data) in enumerate(prompt_data.items(), 1):
        output_file = output_dir / room_data['image_filename']
        
        # Skip if exists
        if skip_existing and output_file.exists():
            print(f"[{idx:2d}/{total_rooms}] ⏭️  {room_data['room_name'][:30]:30} (exists)")
            skipped += 1
            continue
        
        print(f"[{idx:2d}/{total_rooms}] 🎨 {room_data['room_name'][:30]:30}", end=" ")
        
        # Generate the image
        if generate_image(room_data, output_file, api_url, custom_settings):
            generated += 1
        else:
            failed += 1
        
        # Small delay between requests
        if idx < total_rooms:
            time.sleep(0.5)
    
    # Summary
    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"✅ Generated: {generated} images")
    print(f"⏭️  Skipped: {skipped} images (already existed)")
    if failed > 0:
        print(f"❌ Failed: {failed} images")
    print(f"📊 Total: {total_rooms} rooms")
    
    if generated > 0:
        print(f"\n🎮 You can now run the game to see your images!")
        print(f"   python3 temple_runner.py")

def regenerate_single(prompt_data: Dict, output_dir: Path, api_url: str = "http://localhost:7860") -> None:
    """Regenerate a specific room"""
    
    print("\nAvailable rooms:")
    room_list = list(prompt_data.keys())
    for i, room_id in enumerate(room_list, 1):
        room_name = prompt_data[room_id]['room_name']
        print(f"  {i:2d}. {room_name} ({room_id})")
    
    print("\nEnter room number (or 'q' to quit):")
    choice = input("> ").strip()
    
    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(room_list):
            room_id = room_list[idx]
            room_data = prompt_data[room_id]
            output_file = output_dir / room_data['image_filename']
            
            print(f"\n🎨 Regenerating: {room_data['room_name']}")
            if generate_image(room_data, output_file, api_url):
                print(f"✅ Successfully regenerated {room_data['image_filename']}")
            else:
                print(f"❌ Failed to regenerate")
        else:
            print("Invalid room number")
    except ValueError:
        print("Invalid input")

def custom_settings_menu() -> Optional[Dict]:
    """Allow user to customize generation settings"""
    
    print("\n⚙️  CUSTOM SETTINGS (press Enter to use defaults)")
    print("-" * 40)
    
    settings = {}
    
    # Steps
    steps = input("Steps (default: 30): ").strip()
    if steps and steps.isdigit():
        settings['steps'] = int(steps)
    
    # CFG Scale
    cfg = input("CFG Scale (default: 7.5): ").strip()
    if cfg:
        try:
            settings['cfg_scale'] = float(cfg)
        except:
            pass
    
    # Sampler
    sampler = input("Sampler (default: DPM++ 2M Karras): ").strip()
    if sampler:
        settings['sampler_name'] = sampler
    
    # Seed
    seed = input("Seed (default: -1 for random): ").strip()
    if seed and seed.lstrip('-').isdigit():
        settings['seed'] = int(seed)
    
    # Size
    size = input("Size (default: 768x512): ").strip()
    if size and 'x' in size:
        try:
            width, height = size.split('x')
            settings['width'] = int(width)
            settings['height'] = int(height)
        except:
            pass
    
    if settings:
        print("\nUsing custom settings:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    return settings if settings else None

def main():
    """Main execution"""
    prompt_file = '/home/aaron/Projects/games/maze/temple-room-prompts.json'
    api_url = "http://localhost:7860"
    
    # Check for custom API URL argument
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    # Load prompts
    prompt_data = load_prompts(prompt_file)
    
    # Ensure output directory exists
    output_dir = ensure_output_dir()
    
    print("=" * 60)
    print(" LEGENDS OF THE HIDDEN TEMPLE")
    print(" Temple Room Image Generator")
    print("=" * 60)
    print(f"\n📋 Loaded {len(prompt_data)} room prompts")
    print(f"🌐 API URL: {api_url}")
    print(f"📂 Output: {output_dir}\n")
    
    print("Options:")
    print("1. Generate ALL room images")
    print("2. Generate missing rooms only")
    print("3. Regenerate specific room")
    print("4. Generate with custom settings")
    print("5. Check API status")
    print("6. Exit")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == '1':
        print("\n⚠️  This will overwrite existing images!")
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            batch_generate(prompt_data, output_dir, api_url, skip_existing=False)
    
    elif choice == '2':
        batch_generate(prompt_data, output_dir, api_url, skip_existing=True)
    
    elif choice == '3':
        if check_api_status(api_url):
            regenerate_single(prompt_data, output_dir, api_url)
    
    elif choice == '4':
        custom_settings = custom_settings_menu()
        batch_generate(prompt_data, output_dir, api_url, skip_existing=True, 
                      custom_settings=custom_settings)
    
    elif choice == '5':
        if check_api_status(api_url):
            api_info = get_api_info(api_url)
            print(f"\n📦 Current model: {api_info.get('model', 'Unknown')}")
            if 'samplers' in api_info:
                print(f"🎨 Available samplers:")
                for sampler in api_info['samplers'][:10]:
                    print(f"   • {sampler}")
                if len(api_info['samplers']) > 10:
                    print(f"   ... and {len(api_info['samplers']) - 10} more")
    
    elif choice == '6':
        print("\n👋 Goodbye! May Olmec guide your way!")
    
    else:
        print("\n❌ Invalid option")

if __name__ == "__main__":
    main()