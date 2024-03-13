import bpy
import bmesh
import math


#def create_shelf(width, depth, thickness, front_z, back_z, location, wavy=False):
#    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
#    shelf = bpy.context.object
#    shelf.dimensions = [width, depth, thickness]
#    subdivisions = 100

#    if wavy:
#        # Enter edit mode
#        bpy.ops.object.mode_set(mode='EDIT')
#        bm = bmesh.from_edit_mesh(shelf.data)
#        
#        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=subdivisions, use_grid_fill=True)

#        # Apply wave to vertices
#        wave_amplitude = 4.0  # Adjust as needed
#        wave_frequency = 70  # Adjust as needed
#        for vert in bm.verts:
#            vert.co.z += math.sin(vert.co.x * wave_frequency) * wave_amplitude

#        # Update the mesh
#        bmesh.update_edit_mesh(shelf.data)
#        bpy.ops.object.mode_set(mode='OBJECT')

#    # Calculate the angle and adjust position for the shelf
#    angle = math.atan2(front_z - back_z, depth)
#    shelf.rotation_euler[0] = angle
#    z_offset = (front_z + back_z - depth * math.tan(angle)) / 2
#    shelf.location = (location[0], location[1], location[2] + z_offset)

#    return shelf

# Example of creating a wavy shelf
#create_shelf(20.0, 10.0, 0.1, 0.3, 0.1, (0, 0, 1), wavy=True)


def create_shelf(width, shelf_depth, depth, thickness, front_z, back_z, wavy=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,(shelf_depth - depth)/2,0))
    shelf = bpy.context.object
    dz = front_z - back_z
    shelf.dimensions = [width, math.sqrt((shelf_depth - thickness)**2+dz**2), thickness]
    subdivisions = 100

    if wavy:
        wave_amplitude = 4.0  # Adjust as needed
        wave_number = 10  # Adjust as needed
        shelf.dimensions = [width, math.sqrt((shelf_depth + wave_amplitude - thickness)**2+dz**2), thickness]
        dy = wave_amplitude / 2
        dz_wavy = dy * dz / shelf_depth
        shelf.location.y -= dy
        shelf.location.z -= dz_wavy
        # Enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(shelf.data)
        
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=subdivisions, use_grid_fill=True)

        # Apply wave to vertices
        
        for vert in bm.verts:
            vert.co.z += math.sin(vert.co.x / width * 2 * math.pi * 195) * wave_amplitude

        # Update the mesh
        bmesh.update_edit_mesh(shelf.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
    # Calculate the angle based on front and back z-intercepts
    angle = math.atan2(front_z - back_z, shelf_depth)
    shelf.rotation_euler[0] = angle  # Rotate around the X-axis
    print(angle * 180 / math.pi)

    # Adjust shelf location based on the new angle
    z_offset = (back_z + front_z + thickness) / 2
    shelf.location.z += z_offset
    
    if wavy:
        # if wavy, make sure the shelf doesn't protrude out the back
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (-(depth+wave_amplitude)/2), back_z))
        hole = bpy.context.object
        hole.dimensions = [width, wave_amplitude, (wave_amplitude + thickness) * 2]

        # Boolean operation to subtract the protrusion
        mod = shelf.modifiers.new(name="Hole", type='BOOLEAN')
        mod.object = hole
        mod.operation = 'DIFFERENCE'
        bpy.context.view_layer.objects.active = shelf
        bpy.ops.object.modifier_apply(modifier=mod.name)

        # Delete the cylinder
        bpy.data.objects.remove(hole)

    return shelf

def create_perforated_face(size, hole_diameter, hole_spacing, thickness):
    width, depth = size
    num_holes_x = int(width / hole_spacing)
    num_holes_y = int(depth / hole_spacing)

    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name="Perforated_Mesh")
    obj = bpy.data.objects.new("Perforated_Object", mesh)

    # Link object to the scene
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Construct the mesh
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=num_holes_x, y_segments=num_holes_y, size=width / 2)

    # Remove faces for holes
    for x in range(num_holes_x):
        for y in range(num_holes_y):
            hole_center = ((x + 0.5) * hole_spacing - width / 2, (y + 0.5) * hole_spacing - depth / 2)
            for face in bm.faces:
                if all(math.hypot(vert.co.x - hole_center[0], vert.co.y - hole_center[1]) < hole_diameter / 2 for vert in face.verts):
                    bmesh.ops.delete(bm, geom=[face], context='FACES')

    # Extrude the mesh
    bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for vert in bm.verts:
        if vert.select:
            vert.co.z += thickness

    # Update the mesh from bmesh
    bm.to_mesh(mesh)
    bm.free()

    return obj

def add_holes_to_bottom(bottom_obj, width, depth, hole_diameter, hole_spacing):
    # Calculate number of holes based on spacing
    num_holes_x = int(width / hole_spacing)
    num_holes_y = int(depth / hole_spacing)

    for i in range(num_holes_x):
        for j in range(num_holes_y):
            # Position for each hole
            x = (i + 0.5) * hole_spacing - width / 2
            y = (j + 0.5) * hole_spacing - depth / 2

            # Create a cylinder (hole)
            bpy.ops.mesh.primitive_cylinder_add(radius=hole_diameter / 2, depth=5, location=(x, y, 0))
            hole = bpy.context.object

            # Boolean operation to subtract the hole
            mod = bottom_obj.modifiers.new(name="Hole", type='BOOLEAN')
            mod.object = hole
            mod.operation = 'DIFFERENCE'
            bpy.context.view_layer.objects.active = bottom_obj
            bpy.ops.object.modifier_apply(modifier=mod.name)

            # Delete the cylinder
            bpy.data.objects.remove(hole)
            
def create_rack(width, height, depth, shelf_depth, shelf_thickness, shelf_z_intersects):
    # Set units to centimeters
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 0.01
    bpy.context.scene.unit_settings.length_unit = 'CENTIMETERS'

    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Create the back
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -depth/2, height/2))
    back = bpy.context.object
    back.dimensions = [width, shelf_thickness, height]

    # Create the sides
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-(width - shelf_thickness)/2, (shelf_depth - depth)/2, height/2))
    left_side = bpy.context.object
    left_side.dimensions = [shelf_thickness, shelf_depth, height]

    bpy.ops.mesh.primitive_cube_add(size=1, location=((width - shelf_thickness)/2, (shelf_depth - depth)/2, height/2))
    right_side = bpy.context.object
    right_side.dimensions = [shelf_thickness, shelf_depth, height]

    # Create the bottom
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, shelf_thickness/2))
    bottom = bpy.context.object
    bottom.dimensions = [width, depth, shelf_thickness]
    add_holes_to_bottom(bottom, width, depth, 0.5, 1.0)
#    bottom = create_perforated_face([width, depth], hole_diameter, hole_spacing, shelf_thickness)
#    bottom.location = (0, 0, -shelf_thickness / 2)


    # Create shelves
    wavy = True
    for i, (front_z, back_z) in enumerate(shelf_z_intersects):
        shelf_height = height / (len(shelf_z_intersects) + 1) * (i + 1)
        create_shelf(width - 2 * shelf_thickness, shelf_depth, depth, shelf_thickness, front_z, back_z, wavy)
        wavy = False

# Parameters (example values)
width = 22.0  # Width of the rack
height = 16.0  # Height of the rack
depth = 11.8  # Depth of the rack
shelf_depth = 9
shelf_thickness = 0.2  # Thickness of the shelves
shelf_z_intersects = [(16.0, 8.0), (8.0, 0.0)]  # (front_z, back_z) for each shelf
hole_diameter = 0.5
hole_spacing = 1.0

create_rack(width, height, depth, shelf_depth, shelf_thickness, shelf_z_intersects)