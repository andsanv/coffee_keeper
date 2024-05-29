from cryptography import fernet


def read_config():
    with open("config.txt", 'r') as config_file:
        key_path = config_file.readline().split()[-1]

    print(key_path)
    return key_path


def load_key(file_directory: str):
    return open(file_directory, 'rb').read()


def main():
    key = fernet.Fernet.generate_key()

    key_path = read_config()

    with open(key_path, 'wb') as key_file:
        key_file.write(key)

    print(load_key(key_path))



if __name__ == "__main__":
    main()