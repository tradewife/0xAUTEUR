#!/usr/bin/env python3
"""Generate the 6 demo shots for the 0xAUTEUR video."""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add AUTEUR to path
sys.path.insert(0, "/home/kt/AUTEUR")
os.chdir("/home/kt/AUTEUR")

# Load environment
from dotenv import load_dotenv
load_dotenv()

from auteur.knowledge.ontology import (
    ShotSpec, LensSpec, LightSetup, ColorPalette,
    CompositionSpec, MovementSpec, FilmStockProfile,
    ShotSize, ShotAngle, MovementType, SensorFormat,
    AspectRatio, LightQuality, GrainStructure
)
from auteur.pipeline.shot import ShotPipeline
from auteur.providers.registry import ProviderRegistry

# Output directory
output_dir = Path("/home/kt/0xAUTEUR/demo/shots_new")
output_dir.mkdir(parents=True, exist_ok=True)

# Shot configurations
shots = [
    {
        "num": 1,
        "description": "Extreme close-up of a hand writing a single line on paper with a pen, then setting it down. The pen lifts slowly from the paper.",
        "emotional_intent": "Intimate moment of creative birth.",
        "shot_size": ShotSize.EXTREME_CLOSE,
        "focal_length": 100,
        "aperture": 1.4,
        "angle": ShotAngle.EYE_LEVEL,
        "movement": MovementType.STATIC,
        "light_quality": LightQuality.SOFT,
        "grain": GrainStructure.MEDIUM,
        "aspect_ratio": AspectRatio.SCOPE_239,
        "sensor_format": SensorFormat.SUPER_16,
        "duration": 4.0,
        "style_notes": "Single motivated window light from upper left, deep shadow falloff, shallow focus, grainy 16mm texture"
    },
    {
        "num": 2,
        "description": "Fast montage: someone riding subway at night with harsh fluorescent lighting, 3am desk with laptop glow, staring at blank screen. Unglamorous creative struggle. Handheld, unstable.",
        "emotional_intent": "Creative exhaustion. The grind behind the vision.",
        "shot_size": ShotSize.MEDIUM_CLOSE,
        "focal_length": 35,
        "aperture": 2.8,
        "angle": ShotAngle.EYE_LEVEL,
        "movement": MovementType.HANDHELD,
        "light_quality": LightQuality.HARD,
        "grain": GrainStructure.COARSE,
        "aspect_ratio": AspectRatio.STANDARD_169,
        "sensor_format": SensorFormat.SUPER_35,
        "duration": 6.0,
        "style_notes": "Harsh fluorescent, high ISO grain, handheld urgency, documentary realism"
    },
    {
        "num": 3,
        "description": "Split screen: left shows terminal with scrolling MCP tool calls, right shows cinematic shot materializing - figure silhouetted against golden light. Code becoming art.",
        "emotional_intent": "Transformation. Technical precision becoming beauty.",
        "shot_size": ShotSize.WIDE,
        "focal_length": 50,
        "aperture": 2.0,
        "angle": ShotAngle.EYE_LEVEL,
        "movement": MovementType.STATIC,
        "light_quality": LightQuality.MIXED,
        "grain": GrainStructure.FINE,
        "aspect_ratio": AspectRatio.STANDARD_169,
        "sensor_format": SensorFormat.FULL_FRAME,
        "duration": 8.0,
        "style_notes": "Split composition, terminal green-on-black, cinematic warm backlight emerging"
    },
    {
        "num": 4,
        "description": "Three fast cuts: IPFS hash in monospace on black, Base Sepolia block explorer with green checkmark, SpendReceipt event log with glowing CID. Pure information.",
        "emotional_intent": "Proof. Immutability. Verification.",
        "shot_size": ShotSize.INSERT,
        "focal_length": 50,
        "aperture": 5.6,
        "angle": ShotAngle.EYE_LEVEL,
        "movement": MovementType.STATIC,
        "light_quality": LightQuality.AMBIENT,
        "grain": GrainStructure.NONE,
        "aspect_ratio": AspectRatio.STANDARD_169,
        "sensor_format": SensorFormat.FULL_FRAME,
        "duration": 4.0,
        "style_notes": "White monospace on black, terminal aesthetic, clinical precision"
    },
    {
        "num": 5,
        "description": "Side-by-side: same shot shown twice. Right version is recomposed darker, tighter, more intense shadows. New CID appears. Visual iteration proof.",
        "emotional_intent": "Evolution. Market driving art. Feedback loop visible.",
        "shot_size": ShotSize.MEDIUM_CLOSE,
        "focal_length": 85,
        "aperture": 1.4,
        "angle": ShotAngle.LOW,
        "movement": MovementType.DOLLY,
        "light_quality": LightQuality.HARD,
        "grain": GrainStructure.MEDIUM,
        "aspect_ratio": AspectRatio.SCOPE_239,
        "sensor_format": SensorFormat.FULL_FRAME,
        "duration": 4.0,
        "style_notes": "Split comparison, right side tighter, deeper shadows, push in"
    },
    {
        "num": 6,
        "description": "Black screen with white text appearing: '0xauteur.com', 'Pay per shot. USDC. x402.', 'No account. No session. No UI.', 'AUTEUR'. Clean, minimal end card.",
        "emotional_intent": "Clarity. The manifesto. This is what we are.",
        "shot_size": ShotSize.WIDE,
        "focal_length": 50,
        "aperture": 8.0,
        "angle": ShotAngle.EYE_LEVEL,
        "movement": MovementType.STATIC,
        "light_quality": LightQuality.AMBIENT,
        "grain": GrainStructure.NONE,
        "aspect_ratio": AspectRatio.STANDARD_169,
        "sensor_format": SensorFormat.FULL_FRAME,
        "duration": 4.0,
        "style_notes": "Typography, white Helvetica on black, staggered fade-in"
    }
]


async def generate_shot(shot_config, pipeline):
    """Generate a single shot."""
    num = shot_config["num"]
    print(f"\n{'='*60}")
    print(f"SHOT {num}: {shot_config['description'][:50]}...")
    print(f"{'='*60}")
    
    # Build ShotSpec
    spec = ShotSpec(
        description=shot_config["description"],
        emotional_intent=shot_config["emotional_intent"],
       lens=LensSpec(
            focal_length_mm=shot_config["focal_length"],
            max_aperture=shot_config["aperture"],
            character_notes=shot_config["style_notes"]
        ),
        composition=CompositionSpec(
            shot_size=shot_config["shot_size"],
            angle=shot_config["angle"],
            aspect_ratio=shot_config["aspect_ratio"]
        ),
        movement=MovementSpec(
            movement_type=shot_config["movement"]
        ),
        film_stock=FilmStockProfile(
            name=f"AUTEUR Demo Shot {num}",
            sensor_format=shot_config["sensor_format"],
            grain=shot_config["grain"]
        ),
        target_model="kling-3.0",
        animate=True,  # Generate video
        duration_seconds=shot_config["duration"]
    )
    
    print(f"  Model: kling-3.0 (video)")
    print(f"  Duration: {shot_config['duration']}s")
    print(f"  Composition: {shot_config['shot_size'].value} @ {shot_config['focal_length']}mm T{shot_config['aperture']}")
    
    try:
        result = await pipeline.execute(spec, download=True)
        
        if result.success:
            asset = result.primary_asset
            print(f"  ✓ Generated successfully")
            print(f"    Asset URI: {asset.uri if asset else 'N/A'}")
            print(f"    Local path: {asset.local_path if asset and asset.local_path else 'N/A'}")
            
            # Save result metadata
            result_file = output_dir / f"shot_{num}_result.json"
            with open(result_file, 'w') as f:
                json.dump({
                    "shot_num": num,
                    "success": True,
                    "prompt": result.composed.optimized_prompt if result.composed else "",
                    "asset_uri": asset.uri if asset else None,
                    "local_path": str(asset.local_path) if asset and asset.local_path else None,
                    "duration": shot_config["duration"]
                }, f, indent=2)
            
            return True
        else:
            print(f"  ✗ Generation failed")
            if result.video_result:
                print(f"    Error: {result.video_result.error}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("0xAUTEUR Demo Shot Generation")
    print("="*60)
    print(f"Total shots: {len(shots)}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Initialize pipeline
    registry = ProviderRegistry()
    pipeline = ShotPipeline(registry=registry)
    
    print("✓ Pipeline initialized")
    
    # Generate each shot
    results = []
    for shot_config in shots:
        success = await generate_shot(shot_config, pipeline)
        results.append(success)
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Success: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All shots generated successfully")
        print(f"\nNext step: Assemble with voiceover")
        print(f"  Audio: /home/kt/0xAUTEUR/demo/voiceover.mp3")
        print(f"  Shots: {output_dir}/shot_*.mp4")
    else:
        print("\n⚠ Some shots failed - check logs above")


if __name__ == "__main__":
    asyncio.run(main())
