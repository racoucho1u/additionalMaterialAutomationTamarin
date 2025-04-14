import numpy as np 
import matplotlib.pyplot as plt 

# \definecolor{c1}{rgb}{0.45, 0.31, 0.59} %darklavender
# \definecolor{c2}{rgb}{0.75, 0.0, 0.2}   %crimsonglory
# \definecolor{cexpl}{rgb}{0.67, 0.88, 0.69} %celadon
# \definecolor{c4}{rgb}{0.59, 0.78, 0.64} %etonblue
# \definecolor{c5}{rgb}{0.99, 0.84, 0.69} %lightapricot
# \definecolor{copt}{rgb}{0.54, 0.81, 0.94}   %babyblue
# \definecolor{c7}{rgb}{0.57, 0.36, 0.51} %antiquefuchsia
# \definecolor{c8}{rgb}{0.64, 0.64, 0.82} %bluebell
# \definecolor{cdef}{rgb}{0.56, 0.74, 0.56} %darkseagreen
# \definecolor{c10}{rgb}{0.66, 0.89, 0.63} %grannysmithapple
# \definecolor{c11}{rgb}{0.68, 0.87, 0.68} %mossgreen
# \definecolor{c12}{rgb}{0.97, 0.91, 0.56} %flavescent
# \definecolor{cdef}{rgb}{1.0, 0.84, 0.0} %gold(web)(golden)
# \definecolor{cenc}{rgb}{0.99, 0.76, 0.8} %bubblegum

# set width of bar 
barWidth = 0.25
colors=[
(0.54, 0.81, 0.94),
(0.67, 0.88, 0.69),
#(0.97, 0.91, 0.56), #for generalPlot
(1.0, 0.84, 0.0),
#(0.99, 0.84, 0.69), #for generalPlot
(1.0, 0.44, 0.37),
(0.99, 0.76, 0.8),
(0.45, 0.31, 0.59),
(0.9,0.17,0.31)
]
fig = plt.subplots(figsize =(12, 8)) 


# def init():
#     # set height of bar 
#     IT = [12, 30, 1, 8, 22] 
#     ECE = [28, 6, 16, 5, 10] 
#     CSE = [29, 3, 24, 25, 17] 

#     datas = [IT,ECE,CSE]
#     labels = ["_a","b","v"]
#     absName = ["a","b","v"]

#     generatePlot(datas,labels,absName)

def generatePlot0(datas,labels,absName,saveFile="foo.png",barWidth = 0.25):  #data = [IT,ECE,CSE]

     if len(datas) < 2:
         print("no data")
         return()
     if len(absName) != len(datas[0]):
         print("no absName")
         print(len(absName))
         print(len(datas[0]))
         print(absName)
         return()
     if len(labels) < len(datas):
         print("not enough labels")
         return()

     atleasttwo = []
     for i in range(len(datas[0])):
        #  print((datas[0][i],datas[1][i]))
         atleasttwo.append(datas[0][i]-datas[1][i])
    #  print(atleasttwo)

     fig = plt.figure(figsize =(7, 10))

     br1 = np.arange(len(datas[0])) 
     plt.bar(br1, atleasttwo, width = barWidth, color =colors[0],
             edgecolor ='grey', label =labels[0]) 
     # br2 = [x + barWidth for x in br1]
     plt.bar(br1, datas[1], width = barWidth, color =colors[1],
             edgecolor ='grey', label =labels[1], bottom=atleasttwo)

     br = br1
     for i in range (2,len(datas)):
         # Set position of bar on X axis 
         br = [x + barWidth for x in br]
         # Make the plot
         plt.bar(br, datas[i], width = barWidth, color =colors[i],
             edgecolor ='grey', label =labels[i]) 
    

     # Adding Xticks 
     # plt.xlabel('Strategies', fontweight ='bold', fontsize = 12) 
     # plt.ylabel('Lemmas proved', fontweight ='bold', fontsize = 12) 
     plt.xticks([r + barWidth for r in range(len(datas[0]))], 
             absName)

     plt.legend()
     plt.savefig(saveFile)

def generatePlot(datas, labels, absName, saveFile="foo.png", barWidth=0.25):
    # Validate input
    if len(datas) < 2:
        print("no data")
        return
    if len(absName) != len(datas[0]):
        print("no absName")
        print(len(absName))
        print(len(datas[0]))
        print(absName)
        return
    if len(labels) < len(datas):
        print("not enough labels")
        return

    # Calculate the difference between baseline and second dataset
    atleasttwo = []
    for i in range(len(datas[0])):
        atleasttwo.append(datas[0][i] - datas[1][i])

    # Create the figure
    fig = plt.figure(figsize=(10, 7))

    # Position of bars
    br1 = np.arange(len(datas[0]))
    plt.bar(br1, atleasttwo, width=barWidth, color=colors[0],
            edgecolor='grey', label=labels[0])
    plt.bar(br1, datas[1], width=barWidth, color=colors[1],
            edgecolor='grey', label=labels[1], bottom=atleasttwo)

    # Plot additional datasets
    br = br1
    for i in range(2, len(datas)):
        # Set position of bar on X axis
        br = [x + barWidth for x in br]
        # Make the plot
        plt.bar(br, datas[i], width=barWidth, color=colors[i],
                edgecolor='grey', label=labels[i])

    # Add horizontal lines for the baseline
    for i, val in enumerate(datas[0]):  # Assuming datas[0] is the baseline
        plt.hlines(y=val,  # Y-coordinate
                   xmin=i - barWidth,  # Start slightly before the first bar
                   xmax=i + barWidth * (len(datas) - 1),  # End after the last bar
                   color=colors[0],  # Use baseline color
                   linestyles='dashed',  # Dotted line for baseline
                   alpha=0.7)  # Transparency

    # Adding X-ticks
    plt.xticks([r + barWidth for r in range(len(datas[0]))],
               absName)

    # Add legend and save the plot
    plt.legend()
    plt.savefig(saveFile)


def generatePlotGeneral0(datas,labels,absName,saveFile="foo.png",barWidth = 0.11):  #data = [IT,ECE,CSE]

     if len(datas) < 2:
         print("no data")
         return()
     if len(absName) != len(datas[0]):
         print("no absName")
         print(len(absName))
         print(len(datas[0]))
         print(absName)
         return()
     if len(labels) < len(datas):
         print("not enough labels")
         print(labels)
         print(datas)
         return()


     fig = plt.figure(figsize =(15, 10))

     br1 = np.arange(len(datas[0])) 
    #  print(br1)
     plt.bar(br1, datas[0], width = barWidth, color =colors[0],
             edgecolor ='grey', label =labels[0]) 

     br = br1
     for i in range (1,len(datas)):
         # Set position of bar on X axis 
         br = [x + barWidth for x in br]
         # Make the plot
         plt.bar(br, datas[i], width = barWidth, color =colors[i],
             edgecolor ='grey', label =labels[i]) 
    

     # Adding Xticks 
     # plt.xlabel('Branch', fontweight ='bold', fontsize = 15) 
     # plt.ylabel('Students passed', fontweight ='bold', fontsize = 15) 
     plt.xlabel('Strategies', fontweight ='bold', fontsize = 15) 
     plt.ylabel('Number of finished proofs', fontweight ='bold', fontsize = 15) 
     plt.xticks([r + 3*barWidth for r in range(len(datas[0]))], 
             absName)

     plt.legend()
     plt.savefig(saveFile)


def plotSimple(data,absName,saveFile="foo.png",barWidth = 0.25):

    # Figure Size
    fig = plt.figure(figsize =(10, 7))

    # Horizontal Bar Plot
    plt.bar(data,absName,color=(0.67, 0.88, 0.69))
    plt.xlabel('Strategies', fontweight ='bold', fontsize = 10) 
    plt.ylabel('Number of finished proofs', fontweight ='bold', fontsize = 10) 
    plt.savefig(saveFile)

#init()

# import matplotlib.pyplot as plt
# import numpy as np

# colors = ['blue', 'orange', 'green', 'red', 'purple', 'cyan']  # Define your color palette

def generatePlotGeneral(datas, labels, absName, saveFile="foo.png", barWidth=0.11):
    # Validate inputs
    if len(datas) < 2:
        print("no data")
        return
    if len(absName) != len(datas[0]):
        print("no absName")
        print(len(absName))
        print(len(datas[0]))
        print(absName)
        return
    if len(labels) != len(datas):
        print("not enough labels")
        print(len(labels))
        print(len(datas))
        return

    # Create the figure
    fig = plt.figure(figsize=(15, 5))

    # Position of bars
    br1 = np.arange(len(datas[0]))

    # Plot the baseline (not bars, horizontal dashed line)
    for i, val in enumerate(datas[0]):  # Assuming datas[0] is the baseline
        plt.hlines(y=val,  # Y-coordinate for the baseline value
                   xmin=i - barWidth / 2 - 0.1,  # Start slightly before the first bar
                   xmax=i + barWidth * (len(datas) - 1) + 0.05,  # End slightly after the last bar
                   color=colors[-1],  # Use the baseline color
                   linestyles='dashed',  # Dashed line style
                   linewidth=2,  # Thicker dashed line
                   alpha=1)  # Full opacity

    # Plot the other strategies
    plt.bar(br1, datas[1], width=barWidth, color=colors[0],
            edgecolor='grey', label=labels[1])

    br = br1
    for i in range(2, len(datas)):
        # Update bar positions
        br = [x + barWidth for x in br]
        # Plot the bars
        plt.bar(br, datas[i], width=barWidth, color=colors[i-1],
                edgecolor='grey', label=labels[i])

    # Add a proxy artist for the baseline line to the legend
    baseline_proxy = plt.Line2D([0], [0], color=colors[-1], linestyle='dashed', linewidth=2.5, label='Baseline')
    plt.legend(handles=[baseline_proxy] + [plt.Rectangle((0, 0), 1, 1, color=colors[i-1]) for i in range(1, len(labels))],
               labels=['Baseline'] + labels[1:],
               loc='upper left', fontsize=12)

    # Adding X and Y axis labels
    plt.xlabel('Types of lemmas', fontweight='bold', fontsize=15)
    plt.ylabel('Proportion of finished proofs (%)', fontweight='bold', fontsize=15)

    # Adding Xticks
    plt.xticks([r + barWidth * (len(datas) / 2) for r in range(len(datas[0]))],
               absName)

    # Save the plot
    plt.savefig(saveFile)

def generatePlotNoBaseline(datas, labels, absName, saveFile="foo.png", barWidth=0.11):
    # Validate inputs
    if len(datas) < 2:
        print("no data")
        return
    if len(absName) != len(datas[0]):
        print("no absName")
        print(len(absName))
        print(len(datas[0]))
        print(absName)
        return
    if len(labels) != len(datas):
        print("not enough labels")
        print(len(labels))
        print(len(datas))
        return

    # Create the figure
    fig = plt.figure(figsize=(15, 5))

    # Position of bars
    br1 = np.arange(len(datas[0]))

    # Plot the baseline (not bars, horizontal dashed line)
    # for i, val in enumerate(datas[0]):  # Assuming datas[0] is the baseline
    #     plt.hlines(y=val,  # Y-coordinate for the baseline value
    #                xmin=i - barWidth / 2 - 0.1,  # Start slightly before the first bar
    #                xmax=i + barWidth * (len(datas) - 1) + 0.05,  # End slightly after the last bar
    #                color=colors[-1],  # Use the baseline color
    #                linestyles='dashed',  # Dashed line style
    #                linewidth=2,  # Thicker dashed line
    #                alpha=1)  # Full opacity

    # Plot the other strategies
    # plt.bar(br1, datas[0], width=barWidth, color=colors[0],
    #         edgecolor='grey', label=labels[1])

    br = br1
    for i in range(len(datas)):
        # Update bar positions
        br = [x + barWidth for x in br]
        # Plot the bars
        plt.bar(br, datas[i], width=barWidth, color=colors[i-1],
                edgecolor='grey', label=labels[i])

    # Add a proxy artist for the baseline line to the legend
    # baseline_proxy = plt.Line2D([0], [0], color=colors[-1], linestyle='dashed', linewidth=2.5, label='Baseline')
    plt.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=colors[i-1]) for i in range(len(labels))],
               labels=labels,
               loc='upper left', fontsize=12)

    # Adding X and Y axis labels
    plt.xlabel('Types of lemmas', fontweight='bold', fontsize=15)
    plt.ylabel('Proportion of finished proofs (%)', fontweight='bold', fontsize=15)

    # Adding Xticks
    plt.xticks([r + barWidth * (len(datas) / 2) for r in range(len(datas[0]))],
               absName)

    # Save the plot
    plt.savefig(saveFile)

def plotStacked(datas,labels,absName,saveFile="foo.png",barWidth = 0.25):

    if len(datas) == 0:
        print("no data")
        return()
    if len(absName) != len(datas[0]):
        print("no absName")
        print(len(absName))
        print(len(datas))
        print(absName)
        return()
    if len(labels) < len(datas):
        print("not enough labels")
        return()


    N = len(datas[0])
    ind = np.arange(N)   
    width = 0.5 

    base = [datas[0]]
    for i in range(1,len(datas)):
        print(datas[i],base[-1])
        base.append((datas[i][0]+base[-1][0],datas[i][1]+base[-1][1]))

    colors=[(0.67, 0.88, 0.69),(1.0, 0.84, 0.0),(0.54, 0.81, 0.94),(0.99, 0.76, 0.8)]


    fig = plt.subplots(figsize =(5, 10))
    p = [plt.bar(ind, datas[0], width, label =labels[0],color=(0.67, 0.88, 0.69))]
    for i in range(1,len(datas)):
        p.append(plt.bar(ind, datas[i], width,
                 bottom = base[i-1], label =labels[i],color=colors[i]))

    # plt.xlabel('Strategies')
    # plt.ylabel('Number of proved lemmas')
    # plt.title('Contribution by the teams')
    plt.xticks(ind, absName)
    # plt.yticks(np.arange(0, 81, 10))

    plt.legend()
    plt.savefig(saveFile)


#plotStacked()
