# python

import sys

from fbx import *
from FbxCommon import *

def DisplayString(pHeader, pValue="" , pSuffix=""):
    lString = pHeader
    lString += str(pValue)
    lString += pSuffix
    print(lString)

def DisplayBool(pHeader, pValue, pSuffix=""):
    lString = pHeader
    if pValue:
        lString += "true"
    else:
        lString += "false"
    lString += pSuffix
    print(lString)

def DisplayInt(pHeader, pValue, pSuffix=""):
    lString = pHeader
    lString += str(pValue)
    lString += pSuffix
    print(lString)

def DisplayDouble(pHeader, pValue, pSuffix=""):
    print("%s%f%s" % (pHeader, pValue, pSuffix))

def Display2DVector(pHeader, pValue, pSuffix=""):
    print("%s%f, %f%s" % (pHeader, pValue[0], pValue[1], pSuffix))

def Display3DVector(pHeader, pValue, pSuffix=""):
    print("%s%f, %f, %f%s" % (pHeader, pValue[0], pValue[1], pValue[2], pSuffix))

def Display4DVector(pHeader, pValue, pSuffix=""):
    print("%s%f, %f, %f, %f%s" % (pHeader, pValue[0], pValue[1], pValue[2], pValue[3], pSuffix))

def DisplayColor(pHeader, pValue, pSuffix=""):
    print("%s%f (red), %f (green), %f (blue)%s" % (pHeader, pValue.mRed, pValue.mGreen, pValue.mBlue, pSuffix))


def DisplayTextureInfo(pTexture, pBlendMode):
    DisplayString("            Name: \"", pTexture.GetName(), "\"")
    DisplayString("            File Name: \"", pTexture.GetFileName(), "\"")
    
    if 'iOS' in platform:
        filename = str(pTexture.GetFileName())[:-4]
        if '.pvr' in pTexture.GetName():
            pTexture.SetFileName(filename + ".pvr.ccz")
            print filename

    if 'android' in platform:
        filename = str(pTexture.GetFileName())[:-4]
        print filename
        if '.pkm' in pTexture.GetName():
            pTexture.SetFileName(filename + ".pkm")
            print filename

def FindAndDisplayTextureInfoByProperty(pProperty, pDisplayHeader, pMaterialIndex):
    if pProperty.IsValid():
        #Here we have to check if it's layeredtextures, or just textures:
        lLayeredTextureCount = pProperty.GetSrcObjectCount(FbxLayeredTexture.ClassId)
        if lLayeredTextureCount > 0:
            for j in range(lLayeredTextureCount):
                
                DisplayInt("    Layered Texture: ", j)
                lLayeredTexture = pProperty.GetSrcObject(FbxLayeredTexture.ClassId, j)
                lNbTextures = lLayeredTexture.GetSrcObjectCount(FbxTexture.ClassId)
                for k in range(lNbTextures):
                    lTexture = lLayeredTexture.GetSrcObject(FbxTexture.ClassId,k)
                    if lTexture:
                        if pDisplayHeader:
                            DisplayInt("    Textures connected to Material ", pMaterialIndex)
                            pDisplayHeader = False
                            
                        lBlendMode = lLayeredTexture.GetTextureBlendMode(k)
                        DisplayString("    Textures for ", pProperty.GetName())
                        DisplayInt("        Texture ", k)
                        DisplayTextureInfo(lTexture, lBlendMode)
        else:
            # no layered texture simply get on the property
            lNbTextures = pProperty.GetSrcObjectCount(FbxTexture.ClassId)
            for j in range(lNbTextures):
                lTexture = pProperty.GetSrcObject(FbxTexture.ClassId,j)
                if lTexture:
                    # display connectMareial header only at the first time
                    if pDisplayHeader:
                        DisplayInt("    Textures connected to Material ", pMaterialIndex)
                        pDisplayHeader = False
                    
                    DisplayString("    Textures for ", pProperty.GetName().Buffer())
                    DisplayInt("        Texture ", j)  
                    DisplayTextureInfo(lTexture, -1)

        lNbTex = pProperty.GetSrcObjectCount(FbxTexture.ClassId)
        for lTextureIndex in range(lNbTex):
            lTexture = pProperty.GetSrcObject(FbxTexture.ClassId, lTextureIndex) 
                    

def DisplayTexture(pGeometry):
#    for l in range(pGeometry.GetLayerCount()):
#        leVtxc = pGeometry.GetLayer(l).GetVertexColors()
#        leUV = pGeometry.GetLayer(l).GetUVs()
#
#        if leVtxc:
#            header = "            Texture Color (on layer %d): " % l
#            header = header + leVtxc.GetName()
#            print header
#        if leUV:
#            header = "            Texture UV (on layer %d): " % l
#            header = header + leUV.GetName()
#            print header
#            if 'UVSet' in leUV.GetName():
#                leUV.Destroy()
        
    lNbMat = pGeometry.GetNode().GetSrcObjectCount(FbxSurfaceMaterial.ClassId)
    for lMaterialIndex in range(lNbMat):
        lMaterial = pGeometry.GetNode().GetSrcObject(FbxSurfaceMaterial.ClassId, lMaterialIndex)
        lDisplayHeader = True

        if lMaterial:
            print lMaterial.GetName()
            for lTextureIndex in range(FbxLayerElement.sTypeTextureCount()):
                lProperty = lMaterial.FindProperty(FbxLayerElement.sTextureChannelNames(lTextureIndex))
                FindAndDisplayTextureInfoByProperty(lProperty, lDisplayHeader, lMaterialIndex) 


lSdkManager, lScene = InitializeSdkObjects()

platform = None
		
if len(sys.argv) > 2:
    print("\n\nFile: %s\n" % sys.argv[1])
    lResult = LoadScene(lSdkManager, lScene, sys.argv[1])
    platform = sys.argv[2]
else :
    lResult = False

    print("\n\nUsage: ImportScene <FBX file name> Platform: <Platform name (iOS or androind)>")

if not lResult:
    print("\n\nAn error occurred while loading the scene...")
elif not ('android' in platform or 'iOS' in platform):
    print("Platform not recognised")
else :

    lNode = lScene.GetRootNode()

    if lNode:
        for i in range(lNode.GetChildCount()):
            pNode = lNode.GetChild(i)
            lMesh = pNode.GetNodeAttribute ()
            if lMesh == None:
                print("NULL Node Attribute\n")
            else:
                lAttributeType = (lMesh.GetAttributeType())
                if lAttributeType == FbxNodeAttribute.eMesh:
                    DisplayTexture(lMesh)
		
lResult = SaveScene(lSdkManager, lScene, sys.argv[1])
if lResult == False:
    print("\n\nAn error occurred while saving the scene...\n")
    lSdkManager.Destroy()
    sys.exit(1)
        
lSdkManager.Destroy()
sys.exit(0)




