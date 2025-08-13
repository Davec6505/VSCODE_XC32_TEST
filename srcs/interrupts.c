#include <xc.h>

// Global variable to count milliseconds
volatile unsigned int milliseconds = 0;

// Timer1 Interrupt Service Routine
void __attribute__((interrupt(IPL4SRS), vector(_TIMER_1_VECTOR))) Timer1Handler(void)
{
    // Clear the Timer1 interrupt flag
    IFS0bits.T1IF = 0;
    
    // Increment millisecond counter
    milliseconds++;
    
    // Optional: Add your 1ms periodic code here
    // Example: Toggle an LED every 500ms
    if (milliseconds % 500 == 0) {
        LATEbits.LATE0 ^= 1; // Toggle LED1 every 500ms
    }
}
