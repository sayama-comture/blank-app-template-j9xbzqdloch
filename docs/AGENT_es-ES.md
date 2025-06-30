# Agente potenciado por LLM (ReAct)

## ¿Qué es el Agente (ReAct)?

Un Agente es un sistema de IA avanzado que utiliza modelos de lenguaje de gran tamaño (LLM) como su motor computacional central. Combina las capacidades de razonamiento de los LLM con funcionalidades adicionales como planificación y uso de herramientas para realizar tareas complejas de forma autónoma. Los Agentes pueden descomponer consultas complicadas, generar soluciones paso a paso e interactuar con herramientas externas o API para recopilar información o ejecutar subtareas.

Esta muestra implementa un Agente utilizando el enfoque [ReAct (Razonamiento + Acción)](https://www.promptingguide.ai/techniques/react). ReAct permite al agente resolver tareas complejas combinando razonamiento y acciones en un bucle de retroalimentación iterativo. El agente recorre repetidamente tres pasos clave: Pensamiento, Acción y Observación. Analiza la situación actual utilizando el LLM, decide la siguiente acción a tomar, ejecuta la acción utilizando herramientas o API disponibles, y aprende de los resultados observados. Este proceso continuo permite al agente adaptarse a entornos dinámicos, mejorar la precisión de resolución de tareas y proporcionar soluciones conscientes del contexto.

## Caso de Uso de Ejemplo

Un Agente que utiliza ReAct puede aplicarse en diversos escenarios, proporcionando soluciones precisas y eficientes.

### Texto a SQL

Un usuario solicita "el total de ventas del último trimestre". El Agente interpreta esta solicitud, la convierte en una consulta SQL, la ejecuta contra la base de datos y presenta los resultados.

### Previsión Financiera

Un analista financiero necesita hacer una previsión de los ingresos del próximo trimestre. El Agente recopila los datos relevantes, realiza los cálculos necesarios utilizando modelos financieros y genera un informe de previsión detallado, garantizando la precisión de las proyecciones.

## Cómo usar la función de Agente

Para habilitar la funcionalidad de Agente para tu chatbot personalizado, sigue estos pasos:

Hay dos formas de usar la función de Agente:

### Uso de Tool Use

Para habilitar la funcionalidad de Agente con Tool Use para tu chatbot personalizado, sigue estos pasos:

1. Navega a la sección de Agente en la pantalla de bot personalizado.

2. En la sección de Agente, encontrarás una lista de herramientas disponibles que puede utilizar el Agente. De forma predeterminada, todas las herramientas están desactivadas.

3. Para activar una herramienta, simplemente cambia el interruptor junto a la herramienta deseada. Una vez que una herramienta está habilitada, el Agente tendrá acceso a ella y podrá utilizarla al procesar consultas de usuario.

![](./imgs/agent_tools.png)

4. Por ejemplo, la herramienta "Búsqueda en Internet" permite al Agente buscar información en internet para responder preguntas de usuario.

![](./imgs/agent1.png)
![](./imgs/agent2.png)

5. Puedes desarrollar y añadir tus propias herramientas personalizadas para ampliar las capacidades del Agente. Consulta la sección [Cómo desarrollar tus propias herramientas](#how-to-develop-your-own-tools) para obtener más información sobre la creación e integración de herramientas personalizadas.

### Uso de Bedrock Agent

Puedes utilizar un [Agente de Bedrock](https://aws.amazon.com/bedrock/agents/) creado en Amazon Bedrock.

Primero, crea un Agente en Bedrock (por ejemplo, a través de la Consola de Administración). Luego, especifica el ID del Agente en la pantalla de configuración del bot personalizado. Una vez configurado, tu chatbot aprovechará el Agente de Bedrock para procesar consultas de usuario.

![](./imgs/bedrock_agent_tool.png)

## Cómo desarrollar tus propias herramientas

Para desarrollar herramientas personalizadas para el Agente, sigue estas directrices:

- Crea una nueva clase que herede de la clase `AgentTool`. Aunque la interfaz es compatible con LangChain, esta implementación de ejemplo proporciona su propia clase `AgentTool`, de la cual debes heredar ([source](../backend/app/agents/tools/agent_tool.py)).

- Consulta la implementación de ejemplo de una [herramienta de cálculo de IMC](../examples/agents/tools/bmi/bmi.py). Este ejemplo demuestra cómo crear una herramienta que calcula el Índice de Masa Corporal (IMC) basado en la entrada del usuario.

  - El nombre y la descripción declarados en la herramienta se utilizan cuando el LLM considera qué herramienta debe usarse para responder a la pregunta del usuario. En otras palabras, se incrustan en el prompt cuando se invoca al LLM. Por lo tanto, se recomienda describirlos lo más precisamente posible.

- [Opcional] Una vez que hayas implementado tu herramienta personalizada, se recomienda verificar su funcionalidad utilizando un script de prueba ([ejemplo](../examples/agents/tools/bmi/test_bmi.py)). Este script te ayudará a asegurarte de que tu herramienta funciona como se espera.

- Después de completar el desarrollo y las pruebas de tu herramienta personalizada, mueve el archivo de implementación al directorio [backend/app/agents/tools/](../backend/app/agents/tools/). Luego abre [backend/app/agents/utils.py](../backend/app/agents/utils.py) y edita `get_available_tools` para que el usuario pueda seleccionar la herramienta desarrollada.

- [Opcional] Agrega nombres y descripciones claras para el frontend. Este paso es opcional, pero si no lo haces, se utilizarán el nombre y la descripción de la herramienta declarados en tu herramienta. Estos son para el LLM y no para el usuario, por lo que se recomienda agregar una explicación dedicada para mejorar la experiencia de usuario.

  - Edita los archivos i18n. Abre [en/index.ts](../frontend/src/i18n/en/index.ts) y agrega tu propio `name` y `description` en `agent.tools`.
  - Edita también `xx/index.ts`. Donde `xx` representa el código de país que desees.

- Ejecuta `npx cdk deploy` para implementar tus cambios. Esto hará que tu herramienta personalizada esté disponible en la pantalla del bot personalizado.

## Contribución

**¡Las contribuciones al repositorio de herramientas son bienvenidas!** Si desarrollas una herramienta útil y bien implementada, considera contribuirla al proyecto enviando un issue o una pull request.