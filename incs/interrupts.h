#ifndef INTERRUPTS_H
#define INTERRUPTS_H

// Global variable to access millisecond counter
extern volatile unsigned int milliseconds;

// Function prototypes
void Timer1Handler(void);

#endif // INTERRUPTS_H
