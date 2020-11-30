'''
You can run this script by using the command: blender --background --python [path] (if u added blender to the system path)
This script is meant for predicting the prices of a given stl object.
'''
import bpy
#imports for centering function
import mathutils
from mathutils import Vector
#https://blender.stackexchange.com/questions/5210/pointing-the-camera-in-a-particular-direction-programmatically
def main(context):
    '''
    INSERT FILE PATHS ETC. HERE
    ->  IN CASE YOU DON'T EXACTLY KNOW WHAT YOU DOING, DON'T CHANGE ANYTHING ELSE
    '''
    #########################################START########################################
    stl_filepath = "U:\\CAD_Test_Files\\"

    #########################################STOP#########################################

    #For practical purposes, later create a list that will iterate over directories and find stl files
    #for tseting:
    #bpy.ops.import_mesh.stl(filepath="U://CAD Test Files//maßstab.stl")
    #bpy.ops.import_mesh.stl(filepath="U://CAD Test Files//test_stl_feder.stl")
    bpy.ops.import_mesh.stl(filepath="U://CAD_Test_Files//outstl__10010705-B-Modell-MODEL_3D_B3_CN3QU4GY2UGO2S_sdpc.stl")

    #get active object (in case of stl loading the object is already active, so no need to select it)
    b = bpy.context.active_object
    for scene in bpy.data.scenes:
        scene.render.resolution_x = 500
        scene.render.resolution_y = 500
    # get all the karthesian coordiantes and calculate the max x,y,z koordinates for the normalisation scale (the object will be fit into a 10^3 cube)
    x_min = 10000
    x_max = -10000
    y_min = 10000
    y_max = -10000
    z_min = 10000
    z_max = -10000
    scale = 1
    if b.type == 'MESH':
        for vertex in b.data.vertices:
            x = vertex.co.x
            y = vertex.co.y
            z = vertex.co.z
            if(x > x_max):
                x_max = x
            if(x < x_min):
                x_min = x
            if(y > y_max):
                y_max = y
            if(y < y_min):
                y_min = y
            if(z > z_max):
                z_max = z
            if(z < z_min):
                z_min = z
        diff = [abs(x_min-x_max), abs(y_min-y_max), abs(z_min-z_max)]
        scale = 100/max(diff) #we want to divide every axis by the highest difference to set the norm to 100
    #Scale the object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(scale, scale, scale),constraint_axis=(True, True, True),
    mirror              = False,
    proportional_size   = 1,
    snap                = False,
    snap_target         = 'CLOSEST',
    snap_point          = (0, 0, 0),
    snap_align          = False,
    snap_normal         = (0, 0, 0),
    texture_space       = False,
    release_confirm     = True)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    #####Set Cursor to center of gravity
    bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center='MEDIAN')
    ##try to snap the cursor to center
    b.location = (0,0,0)


    #put cursor at origin
    bpy.context.scene.cursor.location       = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))
    ###########SETUP CAMERA#####
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW')
    distance = 200
    camera_locations = [
    [(distance, 0, 0),  (180,270,0)],
    [(0, distance, 0),  (270,180,0)],
    [(0, 0, distance),  (0,0,0)],
    [(-distance, 0, 0), (90,0,270)],
    [(0, -distance, 0), (90,0,0)],
    [(0, 0, -distance), (0,180,270)]
    ]
    pi = 3.14159265
    obj_camera = bpy.data.objects["Camera"]
    # create light datablock, set attributes
    light_data = bpy.data.lights.new(name="light_2.80", type='POINT')
    light_data.energy = 30
    # create new object with our light datablock
    light_object = bpy.data.objects.new(name="light_2.80", object_data=light_data)
    # link light object
    bpy.context.collection.objects.link(light_object)
    # make it active
    bpy.context.view_layer.objects.active = light_object
    #change location
    light_object.location = (200, 200, 200)
    i=0
    for loc in camera_locations:

        obj_camera.location = loc[0]
        obj_camera.rotation_mode = 'XYZ'
        obj_camera.rotation_euler[0] = loc[1][0]*(pi/180.0)
        obj_camera.rotation_euler[1] = loc[1][1]*(pi/180.0)
        obj_camera.rotation_euler[2] = loc[1][2]*(pi/180.0)
        print()
        bpy.data.scenes['Scene'].render.engine = 'BLENDER_WORKBENCH'
        bpy.data.scenes['Scene'].render.filepath = 'U://Database//test_images//testimage'+ str(i) + '.jpg'
        bpy.ops.render.render( write_still=True )
        i=i+1

    bpy.ops.object.align()
    # delete everything
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

class dataPrepRegTool(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.prep_operator"
    bl_label  = "Data Preparation for Regression Tool"
    #Method tests if function can be executed at first
    @classmethod
    def poll(cls, context):
        if bpy.ops.view3d.snap_selected_to_cursor.poll() and bpy.ops.view3d.snap_selected_to_cursor.poll():
            return True
        else:
            return True #########################ONLY TRUE FOR TEST PURPOSES

    def execute(self, context):
        main(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(dataPrepRegTool)
def unregister():
    bpy.utils.unregister_class(dataPrepRegTool)

if __name__ == "__main__":
    register()
    # test call
    bpy.ops.object.prep_operator()
