from systembreach import SystemBreach
import pygame as pg

def main():
    # Create the game instance and start the main loop.
    try:
        sb = SystemBreach()
        sb.run()
    finally:
        pg.quit()

if __name__ == "__main__":
    # Only run automatically when this file is executed directly.
    main()
