#include <xc.h>

// Workaround for IntelliSense if needed (doesn't affect compilation)
#ifndef __XC32__
typedef struct {
    volatile unsigned TRISE0:1;
    volatile unsigned TRISE1:1;
} __TRISEbits_t;
extern volatile __TRISEbits_t TRISEbits;

typedef struct {
    volatile unsigned LATE0:1;
    volatile unsigned LATE1:1;
} __LATEbits_t;
extern volatile __LATEbits_t LATEbits;

typedef struct {
    volatile unsigned COSC:3;
    volatile unsigned :1;
    volatile unsigned NOSC:3;
} __OSCCONbits_t;
extern volatile __OSCCONbits_t OSCCONbits;

// Timer1 register definitions for IntelliSense
typedef struct {
    volatile unsigned TCS:1;
    volatile unsigned TSYNC:1;
    volatile unsigned TCKPS:2;
    volatile unsigned :1;
    volatile unsigned TGATE:1;
    volatile unsigned :9;
    volatile unsigned TSIDL:1;
    volatile unsigned ON:1;
} __T1CONbits_t;
extern volatile __T1CONbits_t T1CONbits;

extern volatile unsigned int TMR1;
extern volatile unsigned int PR1;

// Interrupt control register definitions
typedef struct {
    volatile unsigned T1IP:3;
    volatile unsigned T1IS:2;
} __IPC1bits_t;
extern volatile __IPC1bits_t IPC1bits;

typedef struct {
    volatile unsigned T1IF:1;
} __IFS0bits_t;
extern volatile __IFS0bits_t IFS0bits;

typedef struct {
    volatile unsigned T1IE:1;
} __IEC0bits_t;
extern volatile __IEC0bits_t IEC0bits;

typedef struct {
    volatile unsigned MVEC:1;
} __INTCONbits_t;
extern volatile __INTCONbits_t INTCONbits;

#define __builtin_enable_interrupts() 
#endif

// Configuration bits for PIC32MZ1024EFH064
#pragma config FMIIEN = OFF          // Ethernet RMII/MII Enable (RMII Enabled)
#pragma config FETHIO = ON           // Ethernet I/O Pin Select (Default Ethernet I/O)
#pragma config PGL1WAY = ON          // Permission Group Lock One Way Configuration (Allow only one reconfiguration)
#pragma config PMDL1WAY = ON         // Peripheral Module Disable Configuration (Allow only one reconfiguration)
#pragma config IOL1WAY = ON          // Peripheral Pin Select Configuration (Allow only one reconfiguration)
#pragma config FUSBIDIO = ON         // USB USBID Selection (Controlled by the USB Module)

// DEVCFG2
#pragma config FPLLIDIV = DIV_2      // System PLL Input Divider (2x Divider)
#pragma config FPLLRNG = RANGE_5_10_MHZ // System PLL Input Range (5-10 MHz Input)
#pragma config FPLLICLK = PLL_POSC   // System PLL Input Clock Selection (POSC is input to the System PLL)
#pragma config FPLLMULT = MUL_50     // System PLL Multiplier (PLL Multiply by 50)
#pragma config FPLLODIV = DIV_2      // System PLL Output Clock Divider (2x Divider)
#pragma config UPLLFSEL = FREQ_24MHZ // USB PLL Input Frequency Selection (USB PLL input is 24 MHz)

// DEVCFG1
#pragma config FNOSC = SPLL          // Oscillator Selection Bits (System PLL)
#pragma config DMTINTV = WIN_127_128 // DMT Count Window Interval (Window/Interval value is 127/128 counter value)
#pragma config FSOSCEN = OFF         // Secondary Oscillator Enable (Disable SOSC)
#pragma config IESO = ON             // Internal/External Switch Over (Enabled)
#pragma config POSCMOD = EC          // Primary Oscillator Configuration (External clock mode)
#pragma config OSCIOFNC = OFF        // CLKO Output Signal Active on the OSCO Pin (Disabled)
#pragma config FCKSM = CSECME        // Clock Switching and Monitor Selection (Clock Switch Enabled, FSCM Enabled)
#pragma config WDTPS = PS1048576     // Watchdog Timer Postscaler (1:1048576)
#pragma config WDTSPGM = STOP        // Watchdog Timer Stop During Flash Programming (WDT stops during Flash programming)
#pragma config WINDIS = NORMAL       // Watchdog Timer Window Mode (Watchdog Timer is in non-Window mode)
#pragma config FWDTEN = OFF          // Watchdog Timer Enable (WDT Disabled)
#pragma config FWDTWINSZ = WINSZ_25  // Watchdog Timer Window Size (Window size is 25%)

// DEVCFG0
#pragma config DEBUG = OFF           // Background Debugger Enable (Debugger is disabled)
#pragma config JTAGEN = OFF          // JTAG Enable (JTAG Disabled)
#pragma config ICESEL = ICS_PGx2     // ICE/ICD Comm Channel Select (Communicate on PGEC2/PGED2)
#pragma config TRCEN = ON            // Trace Enable (Trace features in the CPU are enabled)
#pragma config BOOTISA = MIPS32      // Boot ISA Selection (Boot code and Exception code is MIPS32)
#pragma config FECCCON = OFF_UNLOCKED// Dynamic Flash ECC Configuration (ECC and Dynamic ECC are disabled (ECCCON bits are writable))
#pragma config FSLEEP = OFF          // Flash Sleep Mode (Flash is powered down when the device is in Sleep mode)
#pragma config DBGPER = PG_ALL       // Debug Mode CPU Access Permission (Allow CPU access to all permission regions)
#pragma config SMCLR = MCLR_NORM     // Soft Master Clear Enable bit (MCLR pin generates a normal system Reset)
#pragma config SOSCGAIN = GAIN_2X    // Secondary Oscillator Gain Control bits (2x gain setting)
#pragma config SOSCBOOST = ON        // Secondary Oscillator Boost Kick Start Enable bit (Boost the kick start of the oscillator)
#pragma config POSCGAIN = GAIN_2X    // Primary Oscillator Gain Control bits (2x gain setting)
#pragma config POSCBOOST = ON        // Primary Oscillator Boost Kick Start Enable bit (Boost the kick start of the oscillator)
#pragma config EJTAGBEN = NORMAL     // EJTAG Boot (Normal EJTAG functionality)

#define SYS_FREQ 200000000 // 200 MHz

void initClock(void) {
    // Clock is configured through configuration bits
    // System PLL: 10MHz * 50 / 2 / 2 = 200MHz
    // Wait for clock to stabilize
    while(OSCCONbits.COSC != OSCCONbits.NOSC);
}

void initGPIO(void) {
    // Initialize some basic GPIO for LED control
    // Set RE0 and RE1 as outputs (common LED pins on PIC32MZ starter kit)
    TRISEbits.TRISE0 = 0; // RE0 as output
    TRISEbits.TRISE1 = 0; // RE1 as output

    // Initialize outputs to low
    LATEbits.LATE0 = 0; // LED off
    LATEbits.LATE1 = 0; // LED off
}

void initTimer1(void) {
    // Configure Timer1 for 1ms interrupt
    // System Clock = 200MHz, PBCLK3 = 200MHz
    // For 1ms interrupt: 200MHz / 64 / 1000Hz = 3125 counts
    
    // Disable Timer1 during configuration
    T1CONbits.ON = 0;
    
    // Clear Timer1 value
    TMR1 = 0;
    
    // Set Timer1 period for 1ms interrupt
    // PR1 = (PBCLK3 / (Prescaler * Desired_Frequency)) - 1
    // PR1 = (200,000,000 / (64 * 1000)) - 1 = 3124
    PR1 = 3124;
    
    // Configure Timer1 control register
    T1CONbits.TCS = 0;      // Use internal peripheral clock
    T1CONbits.TCKPS = 0b10; // 1:64 prescaler (0b10 = 2 for 1:64)
    T1CONbits.TGATE = 0;    // Gated time accumulation disabled
    T1CONbits.TSIDL = 0;    // Continue operation in idle mode
    
    // Configure Timer1 interrupt
    IPC1bits.T1IP = 4;      // Set Timer1 interrupt priority to 4
    IPC1bits.T1IS = 0;      // Set Timer1 interrupt subpriority to 0
    IFS0bits.T1IF = 0;      // Clear Timer1 interrupt flag
    IEC0bits.T1IE = 1;      // Enable Timer1 interrupt
    
    // Enable multi-vector interrupts
    INTCONbits.MVEC = 1;
    
    // Enable global interrupts
    __builtin_enable_interrupts();
    
    // Enable Timer1
    T1CONbits.ON = 1;
}


