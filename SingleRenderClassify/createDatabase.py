'''
You can run this script by using the command: blender --background --python [path] (if u added blender to the system path)
This script is meant for creating labeled data, for later trainign AIs to predict regression values
'''
import bpy
import os
#imports for centering function
import mathutils
from mathutils import Vector
import numpy
#https://blender.stackexchange.com/questions/5210/pointing-the-camera-in-a-particular-direction-programmatically
pi = 3.14159265

def main(context):
    '''
    INSERT FILE PATHS ETC. HERE
    ->  IN CASE YOU DON'T EXACTLY KNOW WHAT YOU DOING, DON'T CHANGE ANYTHING ELSE
    '''
    #########################################START########################################
    stl_filepath = ""
    databasePath = ""
    alpha_intervall = 90
    beta_intervall  = 180
    gamma_intervall = 180
    bpy.context.preferences.themes[0].view_3d.space.gradients.high_gradient = (100, 100, 100) #set background color for viewport lol

    #Anzahl Bilder = Anzahl Intervalle pro 360 Grad miteinander aufmultipliziert
    #########################################STOP#########################################

    #For practical purposes, later create a list that will iterate over directories and find stl files
    #for tseting:
    #bpy.ops.import_mesh.stl(filepath="U://CAD Test Files//maßstab.stl")

    #bpy.ops.import_mesh.stl(filepath="U://CAD Test Files//test_stl_feder.stl")

    #loop over every dir
    for root, dirs, files in os.walk(stl_filepath, topdown=False):
        #loop over all files
        for name in files:
            #If we find a .stl file -> process it
            if(name.endswith('.stl')):
                print(os.path.join(root, name))
                bpy.ops.import_mesh.stl(filepath=os.path.join(root, name))
                #get active object (in case of stl loading the object is already active, so no need to select it)
                b = bpy.context.active_object

                #assign material to object
                # Get material
                mat = bpy.data.materials.get("spritzguss_gelb")
                # Assign it to object
                if b.data.materials:
                    # assign to 1st material slot
                    b.data.materials[0] = mat
                else:
                    # no slots
                    b.data.materials.append(mat)

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
                ###########SETUP RENDERING#####
                bpy.ops.object.camera_add(enter_editmode=False, align='VIEW')
                obj_camera = bpy.data.objects["Camera"]
                for scene in bpy.data.scenes:
                    #AUFLÖSUNG RESOLUTION
                    scene.render.resolution_x = 400
                    scene.render.resolution_y = 400

                # create light datablock, set attributes
                light_data = bpy.data.lights.new(name="POINTY", type='POINT')
                light_data.energy = 2000000
                # create new object with our light datablock
                light_object = bpy.data.objects.new(name="POINTY", object_data=light_data)
                # link light object
                bpy.context.collection.objects.link(light_object)
                # make it active
                bpy.context.view_layer.objects.active = light_object

                #change location
                light_object.location = (200, 0, 0)
                obj_camera.location   = (200, 0, 0)
                obj_camera.rotation_mode = 'XYZ'
                obj_camera.rotation_euler[0] = 180*(pi/180.0)
                obj_camera.rotation_euler[1] = 270*(pi/180.0)
                obj_camera.rotation_euler[2] = 0




                for alpha in range(0,360,alpha_intervall):
                    for beta in range(0,360,beta_intervall):
                        for gamma in range(0,360,gamma_intervall):
                            #End of amterialset
                            name = os.path.join(databasePath, name)[0:-4]+ str(alpha)+str(beta)+str(gamma) + '.png'
                            print('Rendering '+ name)
                            b.rotation_mode = 'XYZ'
                            b.rotation_euler[0] = alpha
                            b.rotation_euler[1] = beta
                            b.rotation_euler[2] = gamma
                            bpy.data.scenes['Scene'].camera          = obj_camera
                            bpy.data.scenes['Scene'].render.engine   = 'CYCLES'
                            bpy.data.scenes['Scene'].render.filepath = name
                            if(not os.path.isfile(name)):
                                bpy.ops.render.render( write_still=True )
                            print('Render finished\n')
                    #         break
                    #     break
                    # break
                # select all
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete()
                # break





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
