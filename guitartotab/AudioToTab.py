import matplotlib.pyplot as plt
import librosa
import librosa.display
import librosa.feature
import numpy as np

def AudioToTab(y, sr):
    notes = ConvertToNotes(y, sr)
    frets = NotesToFretStart(notes)
    tab = FretsToText(frets)
    return tab


def FretsToText(frets):
    highE = ["E|"]
    B = ["B|"]
    G = ["G|"]
    D = ["D|"]
    A = ["A|"]
    lowE = ["e|"]
    for (x,y) in frets:
        if x == 6:
            highE.append(str(y) + "-")
            B.append("- -")
            G.append("- -")
            D.append("- -")
            A.append("- -")
            lowE.append("- -")

        elif x == 5:
            B.append(str(y) + "-")
            highE.append("- -")
            G.append("- -")
            D.append("- -")
            A.append("- -")
            lowE.append("- -")

        elif x == 4:
            G.append(str(y) + "-")
            B.append("- -")
            highE.append("- -")
            D.append("- -")
            A.append("- -")
            lowE.append("- -")

        elif x == 3:
            D.append(str(y) + "-")
            B.append("- -")
            G.append("- -")
            highE.append("- -")
            A.append("- -")
            lowE.append("- -")

        elif x == 2:
            A.append(str(y) + "-")
            B.append("- -")
            G.append("- -")
            D.append("- -")
            highE.append("- -")
            lowE.append("- -")

        else:
            lowE.append(str(y + "-"))
            B.append("- -")
            G.append("- -")
            D.append("- -")
            A.append("- -")
            highE.append("- -")
    
    tab = ""
    for i in range (len(highE)):
        tab += highE[i]
        
    tab += '\n'
    
    for i in range (len(B)):
        tab += B[i]
    
    tab += "\n"
    
    for i in range (len(G)):
        tab += G[i]
    
    tab += "\n"
    
    for i in range (len(D)):
        tab += D[i]
    
    tab += "\n"

    for i in range (len(A)):
        tab += A[i]
    
    tab += "\n"

    for i in range (len(lowE)):
        tab += lowE[i]
    
    tab += "\n"
    
    return tab



# firstNote takes a bin number and returns the lowest string where note is found
def firstNote(bin):
    if 16 <= bin <= 36:
        return (1, bin - 17)
    elif  36 <= bin <= 41:
        return (2, bin - 22)
    elif  41 <= bin <= 46:
        return (3, bin - 27)
    elif  46 <= bin <= 51:
        return (4, bin - 32)
    elif  51 <= bin <= 55:
        return (5, bin - 36)
    else:
        return (6, bin - 41)
        

# returns true if going from first to second note will result in string change
# takes bin numbers
def newString(first, second, curr_fret):
    dist = second - first
    if curr_fret + dist > 20:
        return True
    elif curr_fret + dist < 0:
        return True
    else:
        return False
    
    
# takes in array of bin numbers and returns an array of string and fret number
# this gets the lowest position on fretboard
def NotesToFretStart(bin_nums):
    curr_string = 1
    frets = []
    prevbin = 0
    for i in range (len(bin_nums)): 
        currbin = bin_nums[i]
        if i == 0: # finds first note, will build fretboard around this note
            curr = firstNote(bin_nums[i])
            frets.append(curr)
            curr_string = curr[0]
            curr_fret = curr[1]
            prevbin = currbin
        elif abs(currbin - prevbin) <= 5: # if next note is within 5 semitones, keep on same string if possible
            dist = currbin - prevbin
            newStr = newString(prevbin, currbin, curr_fret)
            if newStr == False: # if next note can be on same string
                new_fret = curr_fret + dist
                frets.append((curr_string, new_fret))
                prevbin = currbin
                curr_fret += dist
            elif dist < 0: # next note is lower so will go to next lowest string   
                if curr_string == 4 or curr_string == 5: # B and G strings
                    new_fret = curr_fret - dist + 4
                else:
                    new_fret = curr_fret - dist + 5
                curr_string -= 1
                frets.append((curr_string, new_fret))
                prevbin = currbin
                curr_fret = new_fret
            else: # next note is higher so will go to next highest string
                if curr_string == 4 or curr_string == 5: # G and B strings
                    new_fret = curr_fret + dist - 4
                else:
                    new_fret = curr_fret + dist - 5
                curr_string += 1
                frets.append((curr_string, new_fret))
                prevbin = currbin
                curr_fret = new_fret
        else: # if not within 5 semitones move to next string
            dist = currbin - prevbin
            if dist < 0: # go down a string
                if curr_string == 4 or curr_string == 5: # B and G strings
                    new_fret = curr_fret - dist + 4
                else:
                    new_fret = curr_fret - dist + 5
                curr_string -= 1
                frets.append((curr_string, new_fret))
                prevbin = currbin
                curr_fret = new_fret
            else: # go up a string
                if curr_string == 4 or curr_string == 5: # G and B strings
                    new_fret = curr_fret + dist - 4
                else:
                    new_fret = curr_fret + dist - 5
                curr_string += 1
                frets.append((curr_string, new_fret))
                prevbin = currbin
                curr_fret = new_fret
                
    return frets
            


def ConvertToNotes(y, sr): #takes in .wav file and converts to array of notes

    C = np.abs(librosa.cqt(y, sr=sr)) #get cqt values

    maxes = C.max(axis = 0) 
    maxes_ind = C.argmax(axis = 0) 
    
    
    #shift index up 1
    for i in range (len(maxes_ind)):
        maxes_ind[i] += 1 
        
    notes_trial = []
    notes_indexes = []
    notes_mag = []
    prev_note = ""
    prev_note_mag = 0
    
    for i in range (len(maxes_ind)):
        curr_note = bin_to_note(maxes_ind[i])
        curr_note_mag = maxes[i]

        if curr_note_mag > 1.0: #guessing these values, testing what seems to work
            if curr_note_mag > prev_note_mag + 0.9:
                notes_trial.append(curr_note)
                notes_mag.append(maxes[i])
                notes_indexes.append(maxes_ind[i])
                prev_note = curr_note
                prev_note_mag = curr_note_mag
            elif curr_note != prev_note:
                notes_trial.append(curr_note)
                notes_mag.append(maxes[i])
                notes_indexes.append(maxes_ind[i])
                prev_note = curr_note
                prev_note_mag = curr_note_mag
            else:
                prev_note = curr_note
                prev_note_mag = curr_note_mag
            
    
    return notes_indexes


#converts bin (1-84) to note
def bin_to_note(num):
    oct_count = 1
    curr = num
    
    while curr > 12:
        curr = curr - 12
        oct_count += 1
    
    if curr == 1:
        return "C" + str(oct_count)
    elif curr == 2:
        return "C#" + str(oct_count)
    elif curr == 3:
        return "D" + str(oct_count)
    elif curr == 4:
        return "D#" + str(oct_count)
    elif curr == 5:
        return "E" + str(oct_count)
    elif curr == 6:
        return "F" + str(oct_count)
    elif curr == 7:
        return "F#" + str(oct_count)
    elif curr == 8:
        return "G" + str(oct_count)
    elif curr == 9:
        return "G#" + str(oct_count)
    elif curr == 10:
        return "A" + str(oct_count)
    elif curr == 11:
        return "A#" + str(oct_count)
    else:
        return "B" + str(oct_count)
    