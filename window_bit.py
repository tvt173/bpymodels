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
    points = np.array([
        [0, 0],
        [-14, 0],
        [-14, -2],
        [(-14 - 2), (-2 - 1)],
        [-15 + 4, -5],
        # [0, -5],
        # [0, 0],
    ])
    theta = np.linspace(0, np.pi, 50)
    y_sin = -8 * np.sin(theta)
    x_sin = theta * 5 / np.pi
    sin_inner = np.stack([x_sin, y_sin], axis=1)
    sin_inner = sin_inner[::-1]
    sin_inner_ls = sg.LineString(sin_inner)
    sin_outer_ls = sin_inner_ls.offset_curve(1)
    sin_outer = np.array(sin_outer_ls.coords)[::-1]
    # y_sin_outer = y_sin - 1.5
    sin_outer_incl = (sin_outer[:, 1] < -5) | (sin_outer[:, 0] > 2.5)
    sin_outer = sin_outer[sin_outer_incl, :]
    # sin_outer = np.stack([x_sin, y_sin_outer], axis=1)[sin_outer_incl]
    points = np.vstack([sin_inner, points, sin_outer])
    # sin_curve = sg.LineString(np.stack([x_sin, y_sin], axis=1))
    # sin_poly = sin_curve.buffer(0.5)
    # arm_pc = (arm_p1 + arm_p2) * 0.5
    # p_center = sg.Point(arm_pc)
    # circle = p_center.buffer(thickness / 2)
    # poly = sg.Polygon(points)
    # union: sg.Polygon = so.unary_union([sin_poly, poly])
    # return np.array(union.exterior.coords)
    return points

def pill_shape(diameter=5, length=8):
    radius = diameter / 2
    theta = np.linspace(0, np.pi, 50)
    dist = length - diameter
    x = np.cos(theta) * radius
    y = np.sin(theta) * radius + dist/2
    x2 = x[::-1]
    y2 = -y[::-1] - dist
    points = np.stack([np.hstack([x, x2]), np.hstack([y, y2])], axis=1)
    return points


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

def subtract(obj, hole):
    # Boolean operation to subtract the protrusion
    mod = obj.modifiers.new(name="Hole", type='BOOLEAN')
    mod.object = hole
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # Delete the cylinder
    bpy.data.objects.remove(hole)

width =15.0

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

cs = draw_profile()
obj = extrude_cs(cs, extrude_height=width)

hole_cs = pill_shape()
hole = extrude_cs(hole_cs, extrude_height=20)
rotation_matrix = Matrix.Rotation(-np.pi/2, 4, 'X')

# Apply the rotation
obj.matrix_world = obj.matrix_world @ rotation_matrix
rotation_matrix = Matrix.Rotation(-np.pi/2, 4, 'Y')

# Apply the rotation
obj.matrix_world = obj.matrix_world @ rotation_matrix
hole.location.x -= width/2
hole.location.y -= 4
subtract(obj, hole)
bpy.ops.export_mesh.stl(filepath="window_bit.stl")