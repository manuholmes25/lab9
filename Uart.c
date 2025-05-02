#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/pwm.h"
#include "driverlib/uart.h"
#include "driverlib/interrupt.h"
#include "driverlib/rom_map.h"
#include "inc/hw_ints.h"
	

uint32_t g_ui32SysClock;

void UARTSend(const uint8_t *pui8Buffer, uint32_t ui32Count);

void UARTIntHandler(void)
{
    uint32_t ui32Status;
    char c;

    ui32Status = MAP_UARTIntStatus(UART0_BASE, true);
    MAP_UARTIntClear(UART0_BASE, ui32Status);

    while (MAP_UARTCharsAvail(UART0_BASE))
    {
        c = MAP_UARTCharGet(UART0_BASE);

        if (c == 'A') {
            // Encender solo Motor 1 (PWM5 al 50%)
            MAP_PWMOutputState(PWM0_BASE, PWM_OUT_5_BIT, true);
            MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_5, (g_ui32SysClock / 64 / 1000) / 2);
            MAP_PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT, false);
        }
        else if (c == 'B') {
            // Encender ambos motores (PWM5 y PWM6 al 50%)
            MAP_PWMOutputState(PWM0_BASE, PWM_OUT_5_BIT, true);
            MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_5, (g_ui32SysClock / 64 / 1000) / 2);
            MAP_PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT, true);
            MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, (g_ui32SysClock / 64 / 1000) / 2);
        }
        else {
            // Apagar motores
            MAP_PWMOutputState(PWM0_BASE, PWM_OUT_5_BIT, false);
            MAP_PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT, false);
        }
    }
}

void ConfigurarPWM(void)
{
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOG);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_PWM0)) {}
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOG)) {}

    MAP_GPIOPinConfigure(GPIO_PG1_M0PWM5);
    MAP_GPIOPinConfigure(GPIO_PG0_M0PWM4);
    MAP_GPIOPinTypePWM(GPIO_PORTG_BASE, GPIO_PIN_1 | GPIO_PIN_0);

    MAP_PWMClockSet(PWM0_BASE, PWM_SYSCLK_DIV_64);
    uint32_t pwmFreq = 1000;
    uint32_t pwmPeriod = (g_ui32SysClock / 64) / pwmFreq;

    MAP_PWMGenConfigure(PWM0_BASE, PWM_GEN_2, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    MAP_PWMGenPeriodSet(PWM0_BASE, PWM_GEN_2, pwmPeriod);

    MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_5, 0);
    MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, 0);

    MAP_PWMGenEnable(PWM0_BASE, PWM_GEN_2);
}

int main(void)
{
    g_ui32SysClock = MAP_SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ |
                                             SYSCTL_OSC_MAIN |
                                             SYSCTL_USE_PLL |
                                             SYSCTL_CFG_VCO_240), 120000000);

    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);

    MAP_GPIOPinConfigure(GPIO_PA0_U0RX);
    MAP_GPIOPinConfigure(GPIO_PA1_U0TX);
    MAP_GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);

    MAP_UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock, 115200,
                            UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE);

    MAP_IntEnable(INT_UART0);
    MAP_UARTIntEnable(UART0_BASE, UART_INT_RX | UART_INT_RT);
    MAP_IntMasterEnable();

    ConfigurarPWM();

    UARTSend((uint8_t *)"Listo para recibir comandos (A/B)\n", 34);

    while (1) {
        // Espera por interrupciones UART
    }
}

void UARTSend(const uint8_t *pui8Buffer, uint32_t ui32Count)
{
    while (ui32Count--) {
        MAP_UARTCharPutNonBlocking(UART0_BASE, *pui8Buffer++);
    }
}
