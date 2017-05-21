import mdl

import sys

from display import *
from matrix import *
from draw import *

num_frames = 0
basename = 0

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    has_vary = False

    for command in commands:
        if command[0] == "vary":
            has_vary = True
        elif command[0] == "basename":
            basename = command[1]
        elif command[0] == "frames":
            num_frames = command[1]

    if has_vary and (num_frames == 0):
        print "ERROR: frames not set"
        sys.exit()

    if num_frames == 0:
        num_frames = 1

    if basename == 0:
        print "WARNING: BASENAME NOT FOUND"
        basename = "simple"
        print "BASENAME SET TO: simple"



"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    knobs = [ {} for x in range(num_frames) ]

    for command in commands:
        if command[0] == "vary":
            if (int(command[2]) > num_frames) or (int(command[3]) > num_frames):
                print "ERROR: frames for " + command[1] + " out of bounds"
                sys.exit()

        a = int(command[2])
        b = int(command[3])

        if a > b:
            c = b
            b = a
            a = c

        init = float(command[4])
        step = float(command[5])/(b - a + 1)
        for i in range(a, b+1):
            init += step
            knobs[i][command[1]] = init

    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    first_pass( commands )
    knobs = second_pass( commands, num_frames )

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1

    for frame in range(num_frames):
        knob = knobs[frame]

        for command in commands:
            print command
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []

            elif c == 'set':
                if args[0] in knob:
                    knob[args[0]] = float(args[1])

            elif c == 'set_knobs':
                for k in knob.keys():
                    knob[k] = float(args[0])

            #transformations
            elif c == 'move':
                if args[-1] != None and args[-1] in knob:
                    args = [ i * knob[args[-1]] for i in args[:-1] ]

                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []

            elif c == 'scale':
                if args[-1] != None and args[-1] in knob:
                    args = [ i * knob[args[-1]] for i in args[:-1] ]

                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)

                if args[-1] != None and args[-1] in knob:
                    args[1] *= knob[args[-1]]

                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []

            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

            if num_frames > 1:
                save_extension(screen, "anim/" + basename + ("%03d" % frame) + ".png")
                print "Frame saved as anim/" + basename + ("%03d" % frame) + ".png"

            ident(tmp)
            stack = [ [x[:] for x in tmp] ]
            screen = new_screen()
            tmp = []

    if num_frames > 1:
        make_animation( basename )
