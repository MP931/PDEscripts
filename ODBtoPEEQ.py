from odbAccess import openOdb
import csv

def main():
    ### set parameters ###
    models=[
        {
        "fn_odb":'model.odb',
        "frameNum":150,
        "elSetName":'ElSet_ZCenter_NEW',
        "instName":'MODUNIFORM_L25-1',
        },
    ]

    ### run ###
    for model in models:
        fn_odb=model.get("fn_odb")
        frameNum=model.get("frameNum")
        elSetName=model.get("elSetName")
        instName=model.get("instName")
        fieldValueExport(fn_odb, frameNum, elSetName, instName)


def fieldValueExport(fn_odb, frameNum, elSetName, instName):
    #Set output file name
    fn_output='../FieldValueExport/'+fn_odb+'_PEEQ_Center_Frame'+str(frameNum)+'.csv'

    #load odb file and set step
    odb=openOdb(fn_odb) #load odb file
    step1=odb.steps.values()[0] #grab first step
    stepName=step1.name #grab its step name
    print '\n\nStarting to process...', fn_odb, '\n\nStep list:',odb.steps.values() #lists all steps

    """
    #lists all field outputs
    lastFrame = step1.frames[-1]
    print '\nField output list:'
    for fieldName in lastFrame.fieldOutputs.keys():
        print fieldName
    """

    #get PEEQ in field output
    curFrame=step1.frames[frameNum]
    field=curFrame.fieldOutputs['PEEQ']
    fieldVal=field.values
    """
    print '\nValues in PEEQ:', peeqVal[0].__members__ #lists all containing parameters
    for loc in peeq.locations:
        print '\nPEEQ Output point:',loc.position,'\n' #INTEGRATION_POINT
    """

    #get PEEQ of elements only in the specified set
    print 'ElementSet list:', odb.rootAssembly.elementSets.keys() #lists element sets
    center=odb.rootAssembly.elementSets[elSetName] #select elements at the center
    centerField=field.getSubset(region=center)
    centerFieldVal=centerField.values

    # extract element label, PEEQ value, and connected nodes of each element
    op=[] #output cell
    connectivity=[]
    for i, e in enumerate(centerFieldVal):
        op.append([e.elementLabel,e.data])
        connectivity.append(center.elements[0][i].connectivity)
    
    # get node coordinates
    nodes_label=[0]*len(odb.rootAssembly.instances[instName].nodes)
    nodes_coord=[0]*len(odb.rootAssembly.instances[instName].nodes)
    for i, node in enumerate(odb.rootAssembly.instances[instName].nodes):
        nodes_label[i]=node.label
        nodes_coord[i]=node.coordinates

    # get average coordinates of connected nodes
    for i in range(len(op)):
        x,y,z=0,0,0
        for node in connectivity[i]:
            nodes_idx=nodes_label.index(node)
            coord=nodes_coord[nodes_idx]
            x+=coord[0]
            y+=coord[1]
            z+=coord[2]
        x/=len(connectivity[i])
        y/=len(connectivity[i])
        z/=len(connectivity[i])

        op[i].extend([x,y,z])

    # export to csv
    op[0:0]=[['ElementLabel','Weight','x','y','z']] #add column name
    with open(fn_output, 'w') as f:
        w=csv.writer(f, delimiter=',', lineterminator='\n')
        w.writerows(op)
    print '\nFinished export to:', fn_output

    odb.close()

main()
