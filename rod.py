import bpy
import bmesh
import math
import numpy as np
from mathutils import Matrix
import shapely.geometry as sg
import shapely.ops as so

def draw_profile(thickness = 5.0,
                inner_height = 40.0,
                depth = 30.0 + 3,
                beam_length = 100.0,
                angle = 20.0,
                ):
    arm_theta = np.deg2rad(90 - angle)
    arm_theta_perp = arm_theta + np.pi / 2
    arm_p1 = beam_length * np.array([np.cos(arm_theta), np.sin(arm_theta)]) + [depth, thickness]
    arm_p2 = arm_p1 - thickness * np.array([np.cos(arm_theta_perp), np.sin(arm_theta_perp)])
    points = np.array([
        [0, 0],
        [0, thickness],
        [depth, thickness],
        arm_p1,
        arm_p2,
        [depth + thickness, 0],
        [depth + thickness, -(inner_height + thickness)],
        [0, -(inner_height + thickness)],
        [0, -inner_height],
        [depth, -inner_height],
        [depth, 0],
        [0, 0],
    ])
    arm_pc = (arm_p1 + arm_p2) * 0.5
    p_center = sg.Point(arm_pc)
    circle = p_center.buffer(thickness / 2)
    poly = sg.Polygon(points)
    union: sg.Polygon = so.unary_union([circle, poly])
    return np.array(union.exterior.coords)

def extrude_cs(points, extrude_height):
    n_points = points.shape[0]
    vertices = np.zeros((n_points, 3))
    vertices[:, 0:2] = points
    print(vertices)
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

width =20.0

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

cs = draw_profile()
obj = extrude_cs(cs, extrude_height=width)
bpy.ops.export_mesh.stl(filepath="rod.stl")