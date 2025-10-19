🟫 Mini Minecraft — Python Edition

A lightweight, procedurally generated voxel sandbox inspired by Minecraft, built with the Ursina Engine.
This project demonstrates how far Python can go in building a smooth, chunk-based 3D world — including terrain, trees, lighting, and basic player mechanics.

✨ Features

🌍 Procedural Infinite World — terrain generated chunk-by-chunk using Perlin noise

🧱 Dynamic Block System — place and break blocks interactively

🌲 Trees & Nature — auto-generated trees based on height map

☀️ Day–Night Cycle — smooth lighting & sky color transitions

🏃‍♂️ Smooth First-Person Controller — walk, jump, sprint

🔄 Chunk Loading System — loads nearby terrain only, keeps performance stable

⚙️ Optimized Performance — reduced chunk size, progressive rendering

💡 Built from scratch — no dependencies except Ursina!

🎮 Controls
Action	Key
Move	W, A, S, D
Jump	Space
Sprint	Shift
Place Block	Left Mouse
Break Block	Right Mouse
Look Around	Mouse Move
🧩 Requirements

You only need Ursina (no noise module required!):

pip install ursina

🚀 Run the Game
python minecraft.py


Once loaded, the world generates around your spawn point automatically.
You can explore infinitely — chunks load and unload dynamically as you move.

🧠 Code Highlights

Pure Python implementation of Perlin noise

Optimized chunk rendering queue

Procedural tree generation with trunk and layered leaves

Dynamic day–night system driven by time delta

Smooth player acceleration and deceleration

🔮 Future Improvements

Save/load world data to disk

Add biomes (snow, desert, forest)

Implement caves and water

Add basic inventory and hotbar

Simple enemy AI

🧑‍💻 Author

Developed by Hùng Trần — combining curiosity, creativity, and love for procedural generation 🌱
