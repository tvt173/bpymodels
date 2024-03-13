import bpy
import bmesh
import math



def create_hook(width, hook_depth, height, thickness):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,-(hook_depth)/2,0))
    y_start = -(hook_depth)/2
    shelf = bpy.context.object
    shelf.dimensions = [width, hook_depth, thickness]
    subdivisions = 100


    wave_amplitude = height / 7  # Adjust as needed
    wave_number = 0.4  # Adjust as needed
#    shelf.dimensions = [width, math.sqrt((shelf_depth + wave_amplitude - thickness)**2+dz**2), thickness]
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(shelf.data)
    
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=subdivisions, use_grid_fill=True)

    # Apply wave to vertices
    vert_ys = [vert.co.y for vert in bm.verts]
    min_y = min(vert_ys)
    max_y = max(vert_ys)
    y_span = max_y - min_y
    for vert in bm.verts:
        vert.co.z -= math.sin((max_y - vert.co.y)/ y_span * 2 * math.pi * wave_number + math.pi/4) * wave_amplitude

    # Update the mesh
    bmesh.update_edit_mesh(shelf.data)
    bpy.ops.object.mode_set(mode='OBJECT')
#        
#        
#    # Calculate the angle based on front and back z-intercepts
#    angle = math.atan2(front_z - back_z, shelf_depth)
#    shelf.rotation_euler[0] = angle  # Rotate around the X-axis
#    print(angle * 180 / math.pi)

#    # Adjust shelf location based on the new angle
#    z_offset = (back_z + front_z + thickness) / 2
#    shelf.location.z += z_offset
    
#    if wavy:
#        # if wavy, make sure the shelf doesn't protrude out the back
#        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (-(depth+wave_amplitude)/2), back_z))
#        hole = bpy.context.object
#        hole.dimensions = [width, wave_amplitude, (wave_amplitude + thickness) * 2]

#        # Boolean operation to subtract the protrusion
#        mod = shelf.modifiers.new(name="Hole", type='BOOLEAN')
#        mod.object = hole
#        mod.operation = 'DIFFERENCE'
#        bpy.context.view_layer.objects.active = shelf
#        bpy.ops.object.modifier_apply(modifier=mod.name)

#        # Delete the cylinder
#        bpy.data.objects.remove(hole)

    return shelf

            
def create_rack(width, height, depth, shelf_depth, shelf_thickness, hook_depth):

    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Create the back
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    back = bpy.context.object
    back.dimensions = [width, shelf_thickness, height]

    # Create the sides
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (depth-shelf_thickness)/2, (height+shelf_thickness)/2))
    left_side = bpy.context.object
    left_side.dimensions = [width, depth, shelf_thickness]

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (depth-shelf_thickness)/2, -(height+shelf_thickness)/2))
    right_side = bpy.context.object
    right_side.dimensions = [width, depth, shelf_thickness]
    
    create_hook(width, hook_depth, height, shelf_thickness)


# Parameters (example values)
width = 20  # Width of the rack
interference = -0.2
height = 40 - interference  # Height of the rack
depth = 30 + 3  # Depth of the rack
shelf_depth = 9
shelf_thickness = 5  # Thickness of the shelves
shelf_z_intersects = [(16.0, 8.0), (8.0, 0.0)]  # (front_z, back_z) for each shelf
hole_diameter = 0.5
hole_spacing = 1.0
hook_depth = 30

create_rack(width, height, depth, shelf_depth, shelf_thickness, hook_depth)