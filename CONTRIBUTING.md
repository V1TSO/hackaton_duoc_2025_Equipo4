# 🤝 Guía de Contribución / Contributing Guide

Esta guía te ayudará a contribuir al proyecto **hackaton_duoc_2025_Equipo4**.

This guide will help you contribute to the **hackaton_duoc_2025_Equipo4** project.

---

## 📋 Tabla de Contenidos / Table of Contents

- [Español](#español)
  - [Cómo Hacer un Fork del Repositorio](#cómo-hacer-un-fork-del-repositorio)
  - [Configurar tu Entorno Local](#configurar-tu-entorno-local)
  - [Crear una Rama de Trabajo](#crear-una-rama-de-trabajo)
  - [Mantener tu Fork Actualizado](#mantener-tu-fork-actualizado)
  - [Enviar un Pull Request](#enviar-un-pull-request)
- [English](#english)
  - [How to Fork the Repository](#how-to-fork-the-repository)
  - [Set Up Your Local Environment](#set-up-your-local-environment)
  - [Create a Working Branch](#create-a-working-branch)
  - [Keep Your Fork Updated](#keep-your-fork-updated)
  - [Submit a Pull Request](#submit-a-pull-request)

---

## Español

### Cómo Hacer un Fork del Repositorio

Un "fork" es una copia personal del repositorio en tu cuenta de GitHub. Esto te permite hacer cambios sin afectar el proyecto original.

#### Pasos:

1. **Navega al repositorio original**
   - Ve a: https://github.com/V1TSO/hackaton_duoc_2025_Equipo4

2. **Haz clic en el botón "Fork"**
   - En la esquina superior derecha de la página, haz clic en el botón **Fork**
   - Selecciona tu cuenta personal como destino del fork
   - Espera a que GitHub complete el proceso de copia

3. **Verifica tu fork**
   - Ahora deberías tener una copia en: `https://github.com/TU_USUARIO/hackaton_duoc_2025_Equipo4`
   - Esta es tu copia personal donde puedes hacer cambios libremente

### Configurar tu Entorno Local

Una vez que tengas tu fork, necesitas clonarlo a tu computadora local.

#### Pasos:

1. **Clona tu fork**
   ```bash
   git clone https://github.com/TU_USUARIO/hackaton_duoc_2025_Equipo4.git
   cd hackaton_duoc_2025_Equipo4
   ```

2. **Configura el repositorio original como "upstream"**
   
   Esto te permitirá mantener tu fork sincronizado con el proyecto original:
   ```bash
   git remote add upstream https://github.com/V1TSO/hackaton_duoc_2025_Equipo4.git
   ```

3. **Verifica tus repositorios remotos**
   ```bash
   git remote -v
   ```
   
   Deberías ver algo como:
   ```
   origin    https://github.com/TU_USUARIO/hackaton_duoc_2025_Equipo4.git (fetch)
   origin    https://github.com/TU_USUARIO/hackaton_duoc_2025_Equipo4.git (push)
   upstream  https://github.com/V1TSO/hackaton_duoc_2025_Equipo4.git (fetch)
   upstream  https://github.com/V1TSO/hackaton_duoc_2025_Equipo4.git (push)
   ```

4. **Instala las dependencias del proyecto**
   
   Consulta el [README.md](README.md) para instrucciones específicas sobre:
   - Frontend (carpeta `front/`)
   - Backend (carpeta `back/`)
   - Machine Learning (carpeta `ml/`)

### Crear una Rama de Trabajo

Nunca trabajes directamente en la rama `main`. Siempre crea una rama nueva para tus cambios.

#### Pasos:

1. **Asegúrate de estar en la rama main**
   ```bash
   git checkout main
   ```

2. **Actualiza tu rama main**
   ```bash
   git pull upstream main
   ```

3. **Crea una nueva rama descriptiva**
   
   Usa el formato: `feature/descripcion` para nuevas características o `fix/descripcion` para correcciones:
   ```bash
   # Para una nueva característica
   git checkout -b feature/nueva-funcionalidad
   
   # Para una corrección de bug
   git checkout -b fix/correccion-bug
   ```

4. **Haz tus cambios**
   - Edita los archivos necesarios
   - Prueba tus cambios localmente
   - Asegúrate de seguir las convenciones del código existente

5. **Confirma tus cambios**
   ```bash
   git add .
   git commit -m "Descripción clara y concisa de los cambios"
   ```

6. **Sube tu rama a tu fork**
   ```bash
   git push origin feature/nueva-funcionalidad
   ```

### Mantener tu Fork Actualizado

Es importante mantener tu fork sincronizado con el repositorio original.

#### Pasos:

1. **Cambia a la rama main**
   ```bash
   git checkout main
   ```

2. **Obtén los últimos cambios del repositorio original**
   ```bash
   git fetch upstream
   ```

3. **Fusiona los cambios en tu main local**
   ```bash
   git merge upstream/main
   ```

4. **Actualiza tu fork en GitHub**
   ```bash
   git push origin main
   ```

5. **Actualiza tu rama de trabajo (opcional pero recomendado)**
   ```bash
   git checkout feature/nueva-funcionalidad
   git rebase main
   ```

### Enviar un Pull Request

Cuando tus cambios estén listos, puedes solicitar que se fusionen con el proyecto original.

#### Pasos:

1. **Asegúrate de que tu código funciona**
   - Ejecuta todas las pruebas
   - Verifica que no haya errores de linting
   - Prueba la funcionalidad manualmente

2. **Ve a tu fork en GitHub**
   - Navega a: `https://github.com/TU_USUARIO/hackaton_duoc_2025_Equipo4`

3. **Haz clic en "Compare & pull request"**
   - GitHub detectará automáticamente tu rama recién subida
   - O ve a la pestaña "Pull requests" y haz clic en "New pull request"

4. **Completa el formulario del Pull Request**
   - **Título**: Describe brevemente qué hace tu cambio
   - **Descripción**: Explica:
     - ¿Qué problema soluciona?
     - ¿Cómo lo soluciona?
     - ¿Cómo se puede probar?
     - Cualquier detalle relevante

5. **Envía el Pull Request**
   - Haz clic en "Create pull request"
   - Espera la revisión del equipo

6. **Responde a los comentarios**
   - El equipo puede solicitar cambios
   - Haz los cambios en tu rama local
   - Sube los cambios: `git push origin feature/nueva-funcionalidad`
   - El PR se actualizará automáticamente

### 📝 Buenas Prácticas

- **Commits claros**: Escribe mensajes de commit descriptivos
- **Cambios pequeños**: Es mejor hacer varios PRs pequeños que uno gigante
- **Pruebas**: Asegúrate de que tu código funciona antes de enviar el PR
- **Documentación**: Actualiza la documentación si es necesario
- **Código limpio**: Sigue las convenciones de estilo del proyecto

---

## English

### How to Fork the Repository

A "fork" is a personal copy of the repository in your GitHub account. This allows you to make changes without affecting the original project.

#### Steps:

1. **Navigate to the original repository**
   - Go to: https://github.com/V1TSO/hackaton_duoc_2025_Equipo4

2. **Click the "Fork" button**
   - In the upper right corner of the page, click the **Fork** button
   - Select your personal account as the fork destination
   - Wait for GitHub to complete the copy process

3. **Verify your fork**
   - You should now have a copy at: `https://github.com/YOUR_USERNAME/hackaton_duoc_2025_Equipo4`
   - This is your personal copy where you can freely make changes

### Set Up Your Local Environment

Once you have your fork, you need to clone it to your local computer.

#### Steps:

1. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/hackaton_duoc_2025_Equipo4.git
   cd hackaton_duoc_2025_Equipo4
   ```

2. **Set up the original repository as "upstream"**
   
   This will allow you to keep your fork synchronized with the original project:
   ```bash
   git remote add upstream https://github.com/V1TSO/hackaton_duoc_2025_Equipo4.git
   ```

3. **Verify your remote repositories**
   ```bash
   git remote -v
   ```
   
   You should see something like:
   ```
   origin    https://github.com/YOUR_USERNAME/hackaton_duoc_2025_Equipo4.git (fetch)
   origin    https://github.com/YOUR_USERNAME/hackaton_duoc_2025_Equipo4.git (push)
   upstream  https://github.com/V1TSO/hackaton_duoc_2025_Equipo4.git (fetch)
   upstream  https://github.com/V1TSO/hackaton_duoc_2025_Equipo4.git (push)
   ```

4. **Install project dependencies**
   
   Check the [README.md](README.md) for specific instructions about:
   - Frontend (`front/` folder)
   - Backend (`back/` folder)
   - Machine Learning (`ml/` folder)

### Create a Working Branch

Never work directly on the `main` branch. Always create a new branch for your changes.

#### Steps:

1. **Make sure you're on the main branch**
   ```bash
   git checkout main
   ```

2. **Update your main branch**
   ```bash
   git pull upstream main
   ```

3. **Create a new descriptive branch**
   
   Use the format: `feature/description` for new features or `fix/description` for bug fixes:
   ```bash
   # For a new feature
   git checkout -b feature/new-functionality
   
   # For a bug fix
   git checkout -b fix/bug-correction
   ```

4. **Make your changes**
   - Edit the necessary files
   - Test your changes locally
   - Make sure to follow existing code conventions

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Clear and concise description of changes"
   ```

6. **Push your branch to your fork**
   ```bash
   git push origin feature/new-functionality
   ```

### Keep Your Fork Updated

It's important to keep your fork synchronized with the original repository.

#### Steps:

1. **Switch to the main branch**
   ```bash
   git checkout main
   ```

2. **Fetch the latest changes from the original repository**
   ```bash
   git fetch upstream
   ```

3. **Merge the changes into your local main**
   ```bash
   git merge upstream/main
   ```

4. **Update your fork on GitHub**
   ```bash
   git push origin main
   ```

5. **Update your working branch (optional but recommended)**
   ```bash
   git checkout feature/new-functionality
   git rebase main
   ```

### Submit a Pull Request

When your changes are ready, you can request that they be merged with the original project.

#### Steps:

1. **Make sure your code works**
   - Run all tests
   - Verify there are no linting errors
   - Test functionality manually

2. **Go to your fork on GitHub**
   - Navigate to: `https://github.com/YOUR_USERNAME/hackaton_duoc_2025_Equipo4`

3. **Click "Compare & pull request"**
   - GitHub will automatically detect your newly pushed branch
   - Or go to the "Pull requests" tab and click "New pull request"

4. **Complete the Pull Request form**
   - **Title**: Briefly describe what your change does
   - **Description**: Explain:
     - What problem does it solve?
     - How does it solve it?
     - How can it be tested?
     - Any relevant details

5. **Submit the Pull Request**
   - Click "Create pull request"
   - Wait for team review

6. **Respond to comments**
   - The team may request changes
   - Make changes in your local branch
   - Push changes: `git push origin feature/new-functionality`
   - The PR will update automatically

### 📝 Best Practices

- **Clear commits**: Write descriptive commit messages
- **Small changes**: It's better to make several small PRs than one giant one
- **Tests**: Make sure your code works before submitting the PR
- **Documentation**: Update documentation if necessary
- **Clean code**: Follow the project's style conventions

---

## 🆘 ¿Necesitas Ayuda? / Need Help?

Si tienes preguntas o problemas, puedes:

If you have questions or problems, you can:

- Abrir un issue en el repositorio / Open an issue in the repository
- Contactar al equipo / Contact the team
- Revisar la documentación existente / Review existing documentation

---

## 📄 Licencia / License

Al contribuir a este proyecto, aceptas que tus contribuciones serán licenciadas bajo la misma licencia del proyecto.

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

**¡Gracias por contribuir! / Thank you for contributing!** 🎉
