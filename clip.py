import bpy
import bmesh
import math
import numpy as np
from mathutils import Matrix

def create_clip(gap=0.4, thickness=2.0, height=20, tab_length=10, flex_thickness=1.0, width=20):
    # Define the vertices of the polygon (triangle in this case)
    # Each vertex is defined by its x, y, and z coordinates
    theta_start = 180
    theta_end = 60
    theta_end_inner = -90
    n_steps = 30
    inner_radius = gap
    outer_radius = inner_radius + flex_thickness
    theta_outer_arc = np.deg2rad(np.linspace(theta_start, theta_end, n_steps))
    theta_inner_arc = np.deg2rad(np.linspace(theta_end_inner, theta_start, n_steps))
    x_outer= np.cos(theta_outer_arc) * outer_radius
    y_outer = np.sin(theta_outer_arc) * outer_radius
    x_inner = np.cos(theta_inner_arc) * inner_radius
    y_inner = np.sin(theta_inner_arc) * inner_radius
    outer_arc = np.zeros((theta_outer_arc.size, 3))
    inner_arc = np.zeros((theta_inner_arc.size, 3))
    outer_arc[:, 0] = x_outer
    outer_arc[:, 1] = y_outer
    inner_arc[:, 0] = x_inner
    inner_arc[:, 1] = y_inner
    intermediate = np.array([outer_arc[-1, :] + tab_length* np.array([np.cos(theta_outer_arc[-1]), np.sin(theta_outer_arc[-1]), 0]),
                            [0, 0, 0], # placeholder
                            [thickness, 0, 0],
                            [thickness, -height, 0],
                            [0, -height, 0]])
    intermediate[1, :] = intermediate[0, :] + thickness * np.array([np.cos(theta_outer_arc[-1] - np.pi/2), np.sin(theta_outer_arc[-1] - np.pi/2), 0])
    vertices = np.vstack([outer_arc, intermediate, inner_arc])

    # Define the height by which to extrude the polygon
    extrude_height = width

    # Create a new mesh and a new object
    mesh = bpy.data.meshes.new(name='PolygonMesh')
    obj = bpy.data.objects.new('PolygonObject', mesh)

    # Add the object into the scene
    bpy.context.collection.objects.link(obj)

    # Make the object the active object and enter edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Create a new BMesh
    bm = bmesh.new()

    # Add vertices to the BMesh
    for vert in vertices:
        bm.verts.new(vert)

    # Ensure the vertices are ordered correctly and create a face
    bm.verts.ensure_lookup_table()
    bm.faces.new(bm.verts)
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Update the mesh with the new data
    bm.to_mesh(mesh)
    bm.free()  # Free the BMesh to prevent memory leaks

    # Exit edit mode
    #bpy.ops.object.mode_set(mode='OBJECT')

    # Now, extrude the polygon to create a 3D object
    # Get the current mesh
    mesh = obj.data

    # Get the current vertices count before extruding
    verts_start = len(mesh.vertices)

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all faces to be ready for extrusion
    bpy.ops.mesh.select_all(action='SELECT')

    # Perform the extrusion
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, extrude_height)})

    # Go back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj




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
    
#    create_clip(width=width)
#    create_hook(width, hook_depth, height, shelf_thickness)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

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
clip_gap = 0.2

obj = create_clip(gap=clip_gap, width=width, flex_thickness=2.0)
obj.location.z -= width / 2
#    obj.rotation_euler.y -= np.pi / 2
#    obj.rotation_euler.x -= np.pi / 2
rotation_matrix = Matrix.Rotation(-np.pi/2, 4, 'Y')

# Apply the rotation
obj.matrix_world = obj.matrix_world @ rotation_matrix
rotation_matrix = Matrix.Rotation(-np.pi/2, 4, 'Z')

# Apply the rotation
obj.matrix_world = obj.matrix_world @ rotation_matrix

obj.location.x += width/2
obj.location.z += height/2 + shelf_thickness
obj.location.y -= shelf_thickness/2 + clip_gap
create_rack(width, height, depth, shelf_depth, shelf_thickness, hook_depth)

bpy.ops.export_mesh.stl(filepath="clip.stl")