#include <xc.h>
#include "init.h"
#include "interrupts.h"

int main(void) {
    initClock(); // Initialize the clock
    initGPIO();  // Initialize GPIO pins
    initTimer1(); // Initialize Timer1 for 1ms interrupts

    while (1) {
        // Main loop - Timer1 interrupt handles the 1ms timing
        // The LED toggle is now handled in the interrupt service routine
        
        // Example: Toggle LED2 every 1000ms using the millisecond counter
        static unsigned int lastToggle = 0;
        if (milliseconds - lastToggle >= 1000) {
            LATEbits.LATE1 ^= 1; // Toggle LED2
            lastToggle = milliseconds;
        }
        
        // You can add other non-time-critical code here
    }

    return 0;
}
   