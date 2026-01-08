import random
import time

def getName():
    while True:
        name = input("What is your name? ")  #Get's user's name 
        if name == "":
            print("You didn't enter a name!")  #Print's message if no name is entered
            continue
        print("Greetings: " + name)   #Print's user's name
        wait = input("Press Enter to continue...")  #Waits for user to press Enter before closing
        break

def NumGuessVal():
    #randomNumRange = (input("How big do you want to guess between (Default is 100)? ")) #Lets the user put their own number in while still giving the quick option of 100
    #if randomNumRange == "":    #If left blank will make it 100. For the deault option
        #randomNumRange = 100
    #else:                       #If anything else it will convert the string to an integer so it can be used a number
        #randomNumRange = randomNumRange.strip   #Something wrong with this line
        #randomNumRange = int(randomNumRange)    #Something wrong with this line
    randomNum = random.randrange(101)   #Gets a random problem between the number 1 and 100 and lets the user guess it(Fill with randomNumRange when fixed)
    #print(randomNum)    #Prints the random number just to make sure it was working properly
    while True:
        guess = int(input("What is your guess? "))
        if guess == randomNum:                          #If the user gets the number right it will end the code
            print("Wow you got it... ")
            wait = input("Press Enter to continue...")
            break
        elif guess > randomNum:                         #If the user is higher then the number it will tell them it needs to be lower
            print("Needs to be a little bit lower. ")
            continue
        elif guess < randomNum:                         #If the user is lower then the number it will tell them it needs to be higher
            print("Needs to be a little bit higher. ")
            continue

def menu_print():       #Prints the menu for the user to choose where they want to go
    print(" ")
    print("1. Get name")
    print(" ")
    print("2. Number guesser")
    print(" ")
    print("3. Quit")
    print(" ")
    print("4. Animal name")
    print(" ")
    print("5. Password checker")
    print(" ")
    print("6. Dice Game")
    print(" ")

def quit_file():
    quit()

def password_strength_checker():
    if len(input("What is your password? ")) >= 8: 
        print("This is a good password! ")
    else:
        print("This is not a strong password! ")

def dice_game():
    while True:     
        print("Computer Roll Is... ")
        time.sleep(2)
        cpu_guess = random.randrange(6) + 1
        print (cpu_guess)
        wait = input("Press enter to roll the dice... ")
        print("Your Roll Is... ")
        time.sleep(2)
        player_guess = random.randrange(6) + 1
        print(player_guess)
        if player_guess > cpu_guess:
            time.sleep(2)
            print("You Win!!!")
            break
        elif cpu_guess > player_guess:
            time.sleep(2)
            print("You Lose...")
            break
        elif player_guess == cpu_guess:
            time.sleep(2)
            print("It's a tie, go again")
            continue


    

def menu():
    menu_print()
    choice = int(input("Which would you like to choose? "))
    match choice:
        case 1:
            getName()
        case 2:
            NumGuessVal()
        case 3:
            quit()
        case 4:
            animal()
        case 5:
            password_strength_checker()
        case 6:
            dice_game()

def animal_list():
    Sloth = "Sloth"

def animal():
    Sloth_name = "Sloth"
    print ("The name of the sloth is: " + Sloth_name)

    Sloth_name = input("What do you want to name the sloth? ")
    print("The name of the Sloth is now: " + Sloth_name)


#getName()  #Calls the fuction to get user's name (Project #1)
#NumGuessVal()   #Get's a random number and the user has to guess it (Project #2)
while True:
    menu()
    end = input("Do you want it to end (y or n)? ")
    if end == "y":
        break
    elif end == "n":
        continue
    else:
        print("Bad input, going around again!!!")


