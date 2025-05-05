#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/pwm.h"
#include "driverlib/pin_map.h"
#include "driverlib/uart.h"
#include "inc/hw_memmap.h"

char data[100];
uint32_t g_ui32SysClock;

// Enviar string por UART0
void UARTSendString(const char *str) {
    while (*str) {
        UARTCharPut(UART0_BASE, *str++);
    }
}

void PWM_Init(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOG);
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_PWM0));
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOG));

    GPIOPinConfigure(GPIO_PG0_M0PWM4);
    GPIOPinConfigure(GPIO_PG1_M0PWM5);
    GPIOPinTypePWM(GPIO_PORTG_BASE, GPIO_PIN_0 | GPIO_PIN_1);

    PWMClockSet(PWM0_BASE, PWM_SYSCLK_DIV_64);
    uint32_t pwmFreq = 1000;
    uint32_t pwmPeriod = (g_ui32SysClock / 64) / pwmFreq;

    PWMGenConfigure(PWM0_BASE, PWM_GEN_2, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_2, pwmPeriod);

    // Inicia con los PWM apagados (0%)
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, 0);
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_5, 0);

    PWMGenEnable(PWM0_BASE, PWM_GEN_2);
}

int main(void)
{
    g_ui32SysClock = SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ |SYSCTL_OSC_MAIN |SYSCTL_USE_PLL |SYSCTL_CFG_VCO_240), 120000000);

    // UART0
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_UART0));
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTClockSourceSet(UART0_BASE, UART_CLOCK_PIOSC);
    UARTConfigSetExpClk(UART0_BASE, 16000000, 9600,UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE);

    // LEDs (opcional)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);

    // Nueva sección: configurar PK4 y PK5 como salidas
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOK);
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOK));
    GPIOPinTypeGPIOOutput(GPIO_PORTK_BASE, GPIO_PIN_4 | GPIO_PIN_5);

    PWM_Init();

    while (1)
    {
        if (UARTCharsAvail(UART0_BASE)) {
            memset(data, 0, sizeof(data));
            uint32_t i = 0;
            char c;

            while (UARTCharsAvail(UART0_BASE)) {
                c = UARTCharGet(UART0_BASE);
                if (c == '\r') continue;
                if (c == '\n' || i >= sizeof(data) - 1)
                    break;
                data[i++] = c;
            }
            data[i] = '\0';

            if (strcmp(data, "A") == 0) {
                // Encender PWM con 50% duty
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, PWMGenPeriodGet(PWM0_BASE, PWM_GEN_2) / 2);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_5, PWMGenPeriodGet(PWM0_BASE, PWM_GEN_2) / 2);
                PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT | PWM_OUT_5_BIT, true);

                // Encender PK4 y PK5
                GPIOPinWrite(GPIO_PORTK_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4 | GPIO_PIN_5);
            }
            else if (strcmp(data, "C") == 0) {
                // Apagar PWM
                PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT | PWM_OUT_5_BIT, false);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, 0);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_5, 0);

                // Apagar PK4 y PK5
                GPIOPinWrite(GPIO_PORTK_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);
            }

            memset(data, 0, sizeof(data));
        }
    }
}
