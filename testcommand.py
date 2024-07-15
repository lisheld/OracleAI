from newbot import call_command
while True:
    inp = input()
    if inp[0]=='/':
        command = ''
        for char in inp[1:]:
            if char == ' ':
                break
            command += char
        args = inp[len(command)+2:]
        print(call_command(command, args))