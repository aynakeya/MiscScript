#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

typedef unsigned __int32 uint32_t;

typedef int (*DecryptMap)(char const*, char*, uint32_t*);

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("main.exe <encrypted_file>\n");
        return 0;
    }
    char filename[0x50];
    strcpy(filename,argv[1]);
    printf("decrypting file %s\n",filename);

    HINSTANCE hLib;
    DecryptMap decrypt_func;
    DWORD error;

    hLib = LoadLibrary("gpigame.dll");
    if (hLib == NULL) {
        error = GetLastError();
        printf("Error loading gpigame.dll (error code: %d)\n", error);
        return 1;
    }

    printf("load gpigame.dll success\n");
    // Get a pointer to the decrypt() function
    decrypt_func = (DecryptMap) GetProcAddress(hLib, "?DecryptMap@LuaServer@@QAEHPBDPADPAI@Z");
    if (decrypt_func == NULL) {
        printf("Error getting DecryptMap function address\n");
        return 1;
    }
    FILE *input_file = fopen(filename, "rb");

    if (input_file == NULL) {
        printf("Error opening input file\n");
        return 1;
    }

    // Determine the size of the input file
    fseek(input_file, 0, SEEK_END);
    long input_size = ftell(input_file);
    fseek(input_file, 0, SEEK_SET);
    fclose(input_file);

    printf("input size %d\n",input_size);

    char *output_data = (char *) malloc(input_size);


    printf("decrypting....\n");
    uint32_t data_size = 0;
    int result = decrypt_func(filename, output_data, &data_size);
    printf("decrypt result %d\n",result);
    printf("data_size = %d\n",data_size);
    printf("decrypting finished\n");

    strcat(filename,".decrypted");
    FILE *output_file = fopen(filename, "wb");
    if (output_file == NULL) {
        printf("Error opening output file\n");
        free(output_data);
        return 1;
    }

    fwrite(output_data, 1, data_size, output_file);
    fclose(output_file);

    free(output_data);

    FreeLibrary(hLib);

    return 0;
}