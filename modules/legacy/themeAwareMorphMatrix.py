import logging
import random
import pygame

from MetaMindIQTrain.core.scalingHelper import ScalingHelper
from MetaMindIQTrain.core.theme import Theme, ThemeProvider
from MetaMindIQTrain.trainingModule import TrainingModule


class ThemeAwareMorphMatrix(TrainingModule):
    """
    ThemeAwareMorphMatrix implements a pattern recognition module that challenges the user's ability
    to identify specific patterns within a grid. It uses a ScalingHelper for resolution-independence and
    a ThemeProvider to apply consistent UI styling across different platforms.
    """
    def __init__(self, themeProvider: ThemeProvider, screen: pygame.Surface):
        super().__init__()
        self.themeProvider = themeProvider
        self.screen = screen
        self.scalingHelper = ScalingHelper(screen.get_size())
        self.logger = logging.getLogger(__name__)
        
        # Initialize module properties
        self.matrixSize = 4  # 4x4 grid
        self.matrix = self.generateMatrix()
        self.selectedCell = None
        self.feedback = ''

    def generateMatrix(self):
        """
        Generate a random 4x4 matrix with binary values (0 or 1).
        """
        return [[random.randint(0, 1) for _ in range(self.matrixSize)] for _ in range(self.matrixSize)]

    def buildUI(self):
        """
        Construct the UI components: draw the grid of cells using theme-based styles and scaling.
        """
        currentTheme = self.themeProvider.getTheme()
        containerStyle = currentTheme.getStyle('morphMatrix.container')
        cellStyle = currentTheme.getStyle('morphMatrix.cell')
        selectedCellStyle = currentTheme.getStyle('morphMatrix.selectedCell')

        # Draw container background
        pygame.draw.rect(self.screen, containerStyle.get('backgroundColor', (255, 255, 255)), self.screen.get_rect())

        # Define grid parameters
        gridPadding = self.scalingHelper.scaleValue(20)
        cellSize = self.scalingHelper.scaleValue(50)
        
        # Draw grid cells
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                x = gridPadding + j * cellSize
                y = gridPadding + i * cellSize
                rect = pygame.Rect(x, y, cellSize, cellSize)
                
                # Use selected style if this cell is selected
                if self.selectedCell == (i, j):
                    color = selectedCellStyle.get('backgroundColor', (0, 255, 0))
                else:
                    color = cellStyle.get('backgroundColor', (200, 200, 200))

                pygame.draw.rect(self.screen, color, rect, 0)

                # Render cell value as text
                cellValue = self.matrix[i][j]
                fontSize = self.scalingHelper.scaleFontSize(16)
                font = pygame.font.SysFont(None, int(fontSize))
                textColor = cellStyle.get('textColor', (0, 0, 0))
                textSurface = font.render(str(cellValue), True, textColor)
                textRect = textSurface.get_rect(center=rect.center)
                self.screen.blit(textSurface, textRect)

    def update(self, dt: float):
        """
        Update the module state. Currently, this method rebuilds the UI; additional dynamic behaviors
        (such as animations or timed challenges) could be added here.
        """
        self.buildUI()

    def handleInteraction(self, event: pygame.event.Event):
        """
        Process mouse click interactions to determine which cell was selected and provide appropriate feedback.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            gridPadding = self.scalingHelper.scaleValue(20)
            cellSize = self.scalingHelper.scaleValue(50)
            clickedCell = None

            for i in range(self.matrixSize):
                for j in range(self.matrixSize):
                    rect = pygame.Rect(gridPadding + j * cellSize, gridPadding + i * cellSize, cellSize, cellSize)
                    if rect.collidepoint(pos):
                        clickedCell = (i, j)
                        break
                if clickedCell:
                    break

            if clickedCell:
                self.selectedCell = clickedCell
                self.logger.info(f'Cell {clickedCell} selected.')
                # Provide feedback based on cell value; assume 1 is the correct answer
                if self.matrix[clickedCell[0]][clickedCell[1]] == 1:
                    self.feedback = 'Correct!'
                else:
                    self.feedback = 'Try Again!'

    def getFeedback(self) -> str:
        """
        Retrieve feedback generated from the user's interaction.
        """
        return self.feedback


if __name__ == '__main__':
    # Standalone test for ThemeAwareMorphMatrix module
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    
    # For testing, create a simple dark theme instance
    simpleDarkTheme = Theme.createDarkTheme()
    themeProvider = ThemeProvider(simpleDarkTheme)
    
    module = ThemeAwareMorphMatrix(themeProvider, screen)
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            module.handleInteraction(event)
        
        module.update(dt)
        pygame.display.flip()
        
    pygame.quit() 