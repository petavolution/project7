import logging
import random
import pygame

from MetaMindIQTrain.core.scalingHelper import ScalingHelper
from MetaMindIQTrain.core.theme import Theme, ThemeProvider
from MetaMindIQTrain.trainingModule import TrainingModule


class ThemeAwareSymbolMemory(TrainingModule):
    """
    ThemeAwareSymbolMemory implements a symbol memory training exercise where a grid of symbols
    is displayed. The user must recall and select the target symbol. It uses ScalingHelper for
    responsive layout and ThemeProvider to apply consistent styling.
    """
    def __init__(self, themeProvider: ThemeProvider, screen: pygame.Surface):
        super().__init__()
        self.themeProvider = themeProvider
        self.screen = screen
        self.scalingHelper = ScalingHelper(screen.get_size())
        self.logger = logging.getLogger(__name__)

        # Grid setup
        self.gridSize = 3  # 3x3 grid
        self.symbols = ['A', 'B', 'C', 'D', 'E', 'F']
        self.grid = self.generateGrid()
        self.targetSymbol = random.choice(self.symbols)
        self.selectedCell = None
        self.feedback = ''

    def generateGrid(self):
        """
        Generate a grid filled with random symbols.
        """
        grid = []
        for _ in range(self.gridSize):
            row = [random.choice(self.symbols) for _ in range(self.gridSize)]
            grid.append(row)
        return grid

    def buildUI(self):
        """
        Build the UI components using the current theme and scaling settings.
        """
        currentTheme = self.themeProvider.getTheme()
        containerStyle = currentTheme.getStyle('symbolMemory.container')
        cellStyle = currentTheme.getStyle('symbolMemory.cell')
        selectedCellStyle = currentTheme.getStyle('symbolMemory.selectedCell')
        targetStyle = currentTheme.getStyle('symbolMemory.targetSymbol')

        # Draw container background
        pygame.draw.rect(self.screen, containerStyle.get('backgroundColor', (30, 30, 30)), self.screen.get_rect())

        # Define grid parameters
        gridPadding = self.scalingHelper.scaleValue(20)
        cellSize = self.scalingHelper.scaleValue(60)
        
        # Draw grid cells
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                x = gridPadding + j * cellSize
                y = gridPadding + i * cellSize
                rect = pygame.Rect(x, y, cellSize, cellSize)
                
                # Apply selected cell style if applicable
                if self.selectedCell == (i, j):
                    fillColor = selectedCellStyle.get('backgroundColor', (0, 200, 0))
                else:
                    fillColor = cellStyle.get('backgroundColor', (200, 200, 200))

                pygame.draw.rect(self.screen, fillColor, rect, 0)
                
                # Render the symbol text
                symbol = self.grid[i][j]
                fontSize = self.scalingHelper.scaleFontSize(24)
                font = pygame.font.SysFont(None, int(fontSize))
                textColor = cellStyle.get('textColor', (0, 0, 0))
                textSurface = font.render(symbol, True, textColor)
                textRect = textSurface.get_rect(center=rect.center)
                self.screen.blit(textSurface, textRect)

        # Display the target symbol at the top
        fontSize = self.scalingHelper.scaleFontSize(30)
        font = pygame.font.SysFont(None, int(fontSize))
        targetText = f"Find: {self.targetSymbol}"
        textColor = targetStyle.get('textColor', (255, 255, 0))
        textSurface = font.render(targetText, True, textColor)
        textRect = textSurface.get_rect(midtop=(self.screen.get_width() // 2, gridPadding // 2))
        self.screen.blit(textSurface, textRect)

    def update(self, dt: float):
        """
        Update the module state by redrawing the UI. Additional animations can be added later.
        """
        self.buildUI()

    def handleInteraction(self, event: pygame.event.Event):
        """
        Process mouse click events to determine if a cell is selected and provide feedback.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            gridPadding = self.scalingHelper.scaleValue(20)
            cellSize = self.scalingHelper.scaleValue(60)
            clickedCell = None
            
            for i in range(self.gridSize):
                for j in range(self.gridSize):
                    rect = pygame.Rect(gridPadding + j * cellSize, gridPadding + i * cellSize, cellSize, cellSize)
                    if rect.collidepoint(pos):
                        clickedCell = (i, j)
                        break
                if clickedCell:
                    break
            
            if clickedCell:
                self.selectedCell = clickedCell
                selectedSymbol = self.grid[clickedCell[0]][clickedCell[1]]
                self.logger.info(f'Cell {clickedCell} with symbol {selectedSymbol} selected.')
                if selectedSymbol == self.targetSymbol:
                    self.feedback = 'Correct!'
                else:
                    self.feedback = 'Incorrect. Try again!'

    def getFeedback(self) -> str:
        """
        Return the feedback generated from the user's last interaction.
        """
        return self.feedback


if __name__ == '__main__':
    # Standalone test for ThemeAwareSymbolMemory module
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # For testing, create a simple dark theme instance
    simpleDarkTheme = Theme.createDarkTheme()
    themeProvider = ThemeProvider(simpleDarkTheme)
    
    module = ThemeAwareSymbolMemory(themeProvider, screen)
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