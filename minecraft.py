from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math, random

app = Ursina()

# Cấu hình tối ưu
CHUNK = 12  # Giảm xuống cho mượt hơn
VIEW = 2
AMPLITUDE = 6
SCALE = 0.025
GROUND = 0

world = {}
loaded_chunks = set()
noise_cache = {}
trees = []

# Perlin noise
random.seed(12345)
perm = list(range(256))
random.shuffle(perm)
perm = perm * 2

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(a, b, t):
    return a + t * (b - a)

def grad(hash, x, y):
    h = hash & 7
    u = x if h < 4 else y
    v = y if h < 4 else x
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

def perlin_noise(x, y):
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    
    u = fade(xf)
    v = fade(yf)
    
    aa = perm[perm[xi] + yi]
    ab = perm[perm[xi] + yi + 1]
    ba = perm[perm[xi + 1] + yi]
    bb = perm[perm[xi + 1] + yi + 1]
    
    x1 = lerp(grad(aa, xf, yf), grad(ba, xf - 1, yf), u)
    x2 = lerp(grad(ab, xf, yf - 1), grad(bb, xf - 1, yf - 1), u)
    
    return (lerp(x1, x2, v) + 1) / 2

def terrain_height(x, z):
    key = (x, z)
    if key not in noise_cache:
        height = 0
        freq = 1
        amp = 1
        max_val = 0
        
        for i in range(3):
            height += perlin_noise(x * SCALE * freq, z * SCALE * freq) * amp
            max_val += amp
            freq *= 2
            amp *= 0.5
        
        height /= max_val
        noise_cache[key] = int(height * AMPLITUDE + GROUND)
    return noise_cache[key]

# Player
player = FirstPersonController()
player.gravity = 0.8
player.jump_height = 2
player.speed = 4
player.max_speed = 10
player.acceleration = 0.15  # Tăng tốc mượt
player.deceleration = 0.08  # Giảm tốc mượt
player.position = (0, 30, 0)

# Smooth movement
player.smooth_movement = True
player.mouse_sensitivity = Vec2(40, 40)

# Sky và lighting
sky = Sky()
sun = DirectionalLight(shadows=False)  # Tắt shadows cho mượt
sun.look_at(Vec3(1, -1, -1))
ambient = AmbientLight(color=color.rgba(180, 180, 180, 255))

# Chu kỳ ngày đêm
day_time = 0
DAY_CYCLE = 60

def update_day_night():
    global day_time
    t = (day_time % DAY_CYCLE) / DAY_CYCLE
    
    angle = t * 360
    sun_y = math.sin(math.radians(angle))
    sun_x = math.cos(math.radians(angle))
    sun.look_at(Vec3(sun_x, -abs(sun_y), -0.5))
    
    if t < 0.25:
        sky.color = color.rgb(135, 206, 235)
        ambient.color = color.rgba(200, 200, 200, 255)
    elif t < 0.3:
        sky.color = color.rgb(255, 140, 100)
        ambient.color = color.rgba(180, 140, 120, 255)
    elif t < 0.7:
        sky.color = color.rgb(10, 10, 50)
        ambient.color = color.rgba(50, 50, 80, 255)
    elif t < 0.75:
        sky.color = color.rgb(255, 140, 100)
        ambient.color = color.rgba(180, 140, 120, 255)
    else:
        sky.color = color.rgb(135, 206, 235)
        ambient.color = color.rgba(200, 200, 200, 255)

def make_tree(x, z):
    h = terrain_height(x, z)
    trunk_height = 4
    tree_parts = []
    
    # Thân cây
    for y in range(h + 1, h + trunk_height + 1):
        pos = (x, y, z)
        trunk = Entity(
            model='cube',
            color=color.rgb(101, 67, 33),
            position=pos,
            collider='box',
            origin_y=0
        )
        tree_parts.append(trunk)
        world[pos] = trunk
    
    # Lá
    top_y = h + trunk_height + 1
    leaf_color = color.rgb(34, 139, 34)
    
    for layer in range(3):
        y = top_y + layer
        size = 2 - layer
        
        for dx in range(-size, size + 1):
            for dz in range(-size, size + 1):
                if abs(dx) + abs(dz) <= size:
                    pos = (x + dx, y, z + dz)
                    leaf = Entity(
                        model='cube',
                        color=leaf_color,
                        position=pos,
                        collider='box',
                        origin_y=0
                    )
                    tree_parts.append(leaf)
                    world[pos] = leaf
    
    trees.append(tree_parts)

def make_chunk(cx, cz):
    chunk_key = (cx, cz)
    if chunk_key in loaded_chunks:
        return
    
    loaded_chunks.add(chunk_key)
    
    # Tạo terrain data
    for x in range(CHUNK):
        for z in range(CHUNK):
            wx = cx * CHUNK + x
            wz = cz * CHUNK + z
            h = terrain_height(wx, wz)
            
            for y in range(GROUND - 3, h + 1):
                pos = (wx, y, wz)
                world[pos] = True
    
    # Spawn cây
    tree_count = random.randint(0, 2)
    for _ in range(tree_count):
        tree_x = cx * CHUNK + random.randint(2, CHUNK - 3)
        tree_z = cz * CHUNK + random.randint(2, CHUNK - 3)
        h = terrain_height(tree_x, tree_z)
        
        if h > GROUND + 2:
            make_tree(tree_x, tree_z)

def make_block(pos):
    key = tuple(map(int, pos))
    if key in world and world[key] is not True:
        return world[key]
    
    y = key[1]
    
    # Màu theo độ cao
    if y > GROUND + 4:
        block_color = color.rgb(150, 150, 150)
    elif y > GROUND:
        block_color = color.rgb(50, 180, 50)
    elif y > GROUND - 2:
        block_color = color.rgb(101, 67, 33)
    else:
        block_color = color.rgb(80, 80, 80)
    
    block = Entity(
        model='cube',
        texture='white_cube',
        color=block_color,
        position=key,
        collider='box',
        origin_y=0
    )
    
    world[key] = block
    return block

def unload_distant_chunks(px, pz):
    cx, cz = math.floor(px / CHUNK), math.floor(pz / CHUNK)
    to_remove = []
    
    for chunk_key in loaded_chunks:
        cx_loaded, cz_loaded = chunk_key
        dist = max(abs(cx_loaded - cx), abs(cz_loaded - cz))
        if dist > VIEW + 2:
            to_remove.append(chunk_key)
    
    for chunk_key in to_remove:
        loaded_chunks.discard(chunk_key)
        cx_rm, cz_rm = chunk_key
        blocks_to_remove = []
        
        for pos, entity in list(world.items()):
            if isinstance(pos, tuple) and len(pos) == 3:
                x, y, z = pos
                in_chunk = (cx_rm * CHUNK <= x < (cx_rm + 1) * CHUNK and 
                           cz_rm * CHUNK <= z < (cz_rm + 1) * CHUNK)
                
                if in_chunk and entity is not True:
                    destroy(entity)
                    blocks_to_remove.append(pos)
        
        for pos in blocks_to_remove:
            world.pop(pos, None)

def render_chunk_blocks(cx, cz):
    rendered = 0
    max_per_call = 50  # Giới hạn render mỗi lần
    
    for x in range(CHUNK):
        for z in range(CHUNK):
            if rendered >= max_per_call:
                return False  # Chưa xong
            
            wx = cx * CHUNK + x
            wz = cz * CHUNK + z
            h = terrain_height(wx, wz)
            
            # Chỉ render top layer
            pos = (wx, h, wz)
            if pos in world and world[pos] is True:
                make_block(pos)
                rendered += 1
            
            # Render 1-2 layer dưới nếu cần
            for y in range(max(h - 2, GROUND - 3), h):
                pos = (wx, y, wz)
                if pos in world and world[pos] is True:
                    # Check nếu exposed
                    neighbors = [
                        (wx + 1, y, wz), (wx - 1, y, wz),
                        (wx, y, wz + 1), (wx, y, wz - 1)
                    ]
                    for n in neighbors:
                        if n not in world or world[n] is True:
                            make_block(pos)
                            rendered += 1
                            break
    
    return True  # Xong

update_counter = 0
render_queue = []
current_render = None

def update():
    global update_counter, render_queue, day_time, current_render
    update_counter += 1
    day_time += time.dt
    
    # Cập nhật ngày đêm mỗi 10 frames
    if update_counter % 10 == 0:
        update_day_night()
    
    px, py, pz = player.position
    
    # Load chunks mỗi 15 frames
    if update_counter % 15 == 0:
        cx, cz = math.floor(px / CHUNK), math.floor(pz / CHUNK)
        
        # Load theo khoảng cách (gần trước, xa sau)
        chunks_to_load = []
        for x in range(cx - VIEW, cx + VIEW + 1):
            for z in range(cz - VIEW, cz + VIEW + 1):
                dist = abs(x - cx) + abs(z - cz)
                chunks_to_load.append((dist, x, z))
        
        chunks_to_load.sort()
        
        for dist, x, z in chunks_to_load:
            chunk_key = (x, z)
            if chunk_key not in loaded_chunks:
                make_chunk(x, z)
                if chunk_key not in render_queue:
                    render_queue.append(chunk_key)
    
    # Progressive render - render từng chút mỗi frame
    if current_render:
        if render_chunk_blocks(*current_render):
            current_render = None
    
    if not current_render and render_queue:
        current_render = render_queue.pop(0)
    
    # Unload chunks mỗi 90 frames
    if update_counter % 90 == 0:
        unload_distant_chunks(px, pz)
    
    # Tốc độ di chuyển mượt hơn
    if held_keys['shift']:
        player.speed = min(player.speed + 0.2, 8)  # Tăng dần
    else:
        player.speed = max(player.speed - 0.15, 4)  # Giảm dần
    
    # Giới hạn tốc độ rơi để không bị glitch
    if player.velocity_y < -1:
        player.velocity_y = -1

def input(key):
    if mouse.hovered_entity and mouse.hovered_entity in world.values():
        b = mouse.hovered_entity
        
        if key == 'left mouse down':
            new_pos = b.position + mouse.normal
            make_block(new_pos)
            
        elif key == 'right mouse down':
            pos = tuple(map(int, b.position))
            if pos in world:
                entity = world[pos]
                if entity is not True:
                    destroy(entity)
                    world.pop(pos, None)

# Pre-load spawn area
print("Đang tạo thế giới...")
for x in range(-VIEW, VIEW + 1):
    for z in range(-VIEW, VIEW + 1):
        make_chunk(x, z)

print("Đang render địa hình...")
for x in range(-VIEW, VIEW + 1):
    for z in range(-VIEW, VIEW + 1):
        while not render_chunk_blocks(x, z):
            pass

# Set player position sau khi terrain đã load
spawn_height = terrain_height(0, 0) + 3
player.position = (0, spawn_height, 0)

print("Hoàn tất! Bắt đầu game...")
app.run()