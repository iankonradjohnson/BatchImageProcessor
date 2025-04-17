# Greyscale Binary Separator: Architecture Design Document

## 1. System Overview

The Greyscale Binary Separator is a system designed to automatically detect and separately process grayscale and binary regions in document images. This approach solves the challenge of applying different thresholding and dithering techniques to different parts of the same image, mimicking the manual process currently performed in Photoshop.

### 1.1 High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                  Greyscale Binary Separator                        │
└───────────────┬───────────────────────────────┬───────────────────┘
                │                               │
                ▼                               ▼
┌───────────────────────────┐     ┌───────────────────────────────┐
│  Region Detection Engine  │     │  Region Processing Engine     │
└─────────────┬─────────────┘     └─────────────┬─────────────────┘
              │                                  │
              ▼                                  ▼
┌─────────────────────────────┐   ┌───────────────────────────────┐
│ Detection Strategy Provider │   │ Processing Strategy Provider  │
└───┬─────────┬─────────┬─────┘   └─────┬─────────┬───────────────┘
    │         │         │               │         │
    ▼         ▼         ▼               ▼         ▼
┌──────┐  ┌──────┐  ┌──────┐       ┌──────┐  ┌──────────┐
│Hist. │  │Texture│  │Edge  │       │Binary│  │Grayscale │
│Anal. │  │Anal.  │  │Detect│       │Proc. │  │Proc.     │
└──────┘  └──────┘  └──────┘       └──────┘  └──────────┘
```

The system follows a layered architecture with clear separation of concerns:

1. **Presentation Layer**: Configuration and user interaction components
2. **Application Layer**: Main processor and coordination logic
3. **Domain Layer**: Core detection and processing engines
4. **Infrastructure Layer**: Image processing utilities and external library integrations

### 1.2 Key Design Decisions

Based on our comprehensive analysis in Phases 1 and 2, we have made the following key design decisions:

1. **Multi-stage Hybrid Pipeline for Detection**: Combining multiple detection techniques (histogram analysis, texture analysis, edge detection) in a configurable pipeline provides the best balance of accuracy, flexibility, and maintainability.

2. **Pipeline Architecture for Processing**: A pipeline approach for processing detected regions provides flexibility in applying different processing steps based on region type.

3. **Strategy Pattern for Algorithms**: Implementing detection and processing strategies using the Strategy pattern enables easy extension with new algorithms without modifying existing code.

4. **Factory Pattern for Component Creation**: Using factories to create strategy instances promotes loose coupling and facilitates configuration-driven behavior.

5. **Facade Pattern for Subsystems**: Providing simplified interfaces to complex subsystems (detection and processing engines) improves usability and maintainability.

### 1.3 SOLID Principles Application

The architecture strictly adheres to SOLID principles:

1. **Single Responsibility Principle**: Each component has a clearly defined responsibility. For example, the Region Detection Engine is solely responsible for identifying different regions in an image, while the Region Processing Engine is responsible for applying appropriate processing to these regions.

2. **Open/Closed Principle**: The system is open for extension but closed for modification. New detection or processing strategies can be added without modifying existing code.

3. **Liskov Substitution Principle**: All strategy implementations are interchangeable within their respective interfaces.

4. **Interface Segregation Principle**: Interfaces are focused and minimal, with each defining only the methods required for its specific role.

5. **Dependency Inversion Principle**: High-level modules depend on abstractions, not concrete implementations, facilitated by dependency injection.

## 2. Component Architecture

### 2.1 Region Detection Engine

The Region Detection Engine is responsible for identifying and segmenting grayscale and binary regions in an input image.

#### 2.1.1 Class Diagram

```
┌───────────────────────────┐
│   RegionDetectionEngine   │
├───────────────────────────┤
│ - strategy_provider       │
│ - config                  │
├───────────────────────────┤
│ + detect_regions()        │
│ + configure()             │
│ + visualize_regions()     │
└─────────────┬─────────────┘
              │ uses
              ▼
┌───────────────────────────┐       ┌───────────────────────┐
│ DetectionStrategyProvider │       │  «interface»          │
├───────────────────────────┤       │  DetectionStrategy    │
│ - strategies              │       ├───────────────────────┤
├───────────────────────────┤       │ + analyze()           │
│ + get_strategy()          │◄──────│ + configure()         │
│ + register_strategy()     │       └───────────────────────┘
│ + get_strategies()        │                 ▲
└───────────────────────────┘                 │
                                              │
               ┌────────────────┬─────────────┴────────────┐
               │                │                          │
  ┌─────────────────────┐┌─────────────────────┐┌─────────────────────┐
  │HistogramAnalysis    ││TextureAnalysis      ││EdgeDetection        │
  │Strategy             ││Strategy             ││Strategy              │
  ├─────────────────────┤├─────────────────────┤├─────────────────────┤
  │+ analyze()          ││+ analyze()          ││+ analyze()          │
  │+ configure()        ││+ configure()        ││+ configure()        │
  └─────────────────────┘└─────────────────────┘└─────────────────────┘
```

#### 2.1.2 Key Components

1. **RegionDetectionEngine**: Facade for the detection subsystem, coordinating the detection process.
   - Responsibilities: Orchestrate the detection pipeline, combine results from multiple strategies, apply post-processing.
   - Interface: `detect_regions(image) -> region_mask`, `configure(parameters) -> None`, `visualize_regions(image, region_mask) -> visualization`

2. **DetectionStrategyProvider**: Factory for detection strategies.
   - Responsibilities: Create, configure, and manage detection strategy instances.
   - Interface: `get_strategy(strategy_name) -> DetectionStrategy`, `register_strategy(strategy_name, strategy_class) -> None`

3. **DetectionStrategy**: Interface for all detection algorithms.
   - Responsibilities: Define common interface for region detection strategies.
   - Interface: `analyze(image) -> region_probabilities`, `configure(parameters) -> None`

4. **Concrete Strategy Implementations**:
   - **HistogramAnalysisStrategy**: Identifies regions based on histogram characteristics.
   - **TextureAnalysisStrategy**: Identifies regions based on texture features.
   - **EdgeDetectionStrategy**: Identifies region boundaries based on edge characteristics.

### 2.2 Region Processing Engine

The Region Processing Engine is responsible for applying appropriate processing to detected regions based on their type.

#### 2.2.1 Class Diagram

```
┌───────────────────────────┐
│   RegionProcessingEngine  │
├───────────────────────────┤
│ - strategy_provider       │
│ - config                  │
├───────────────────────────┤
│ + process_regions()       │
│ + configure()             │
└─────────────┬─────────────┘
              │ uses
              ▼
┌───────────────────────────┐       ┌───────────────────────┐
│ProcessingStrategyProvider │       │  «interface»          │
├───────────────────────────┤       │  ProcessingStrategy   │
│ - strategies              │       ├───────────────────────┤
├───────────────────────────┤       │ + process()           │
│ + get_strategy()          │◄──────│ + configure()         │
│ + register_strategy()     │       └───────────────────────┘
│ + get_strategies()        │                 ▲
└───────────────────────────┘                 │
                                              │
                            ┌─────────────────┴─────────────────┐
                            │                                   │
                 ┌─────────────────────┐           ┌─────────────────────┐
                 │BinaryProcessing     │           │GrayscaleProcessing  │
                 │Strategy             │           │Strategy             │
                 ├─────────────────────┤           ├─────────────────────┤
                 │+ process()          │           │+ process()          │
                 │+ configure()        │           │+ configure()        │
                 └─────────────────────┘           └─────────────────────┘
```

#### 2.2.2 Key Components

1. **RegionProcessingEngine**: Facade for the processing subsystem, coordinating the processing of different regions.
   - Responsibilities: Apply appropriate processing to each region type, merge processed regions.
   - Interface: `process_regions(image, region_mask) -> processed_image`, `configure(parameters) -> None`

2. **ProcessingStrategyProvider**: Factory for processing strategies.
   - Responsibilities: Create, configure, and manage processing strategy instances.
   - Interface: `get_strategy(region_type) -> ProcessingStrategy`, `register_strategy(region_type, strategy_class) -> None`

3. **ProcessingStrategy**: Interface for all processing algorithms.
   - Responsibilities: Define common interface for region processing strategies.
   - Interface: `process(image, region_mask) -> processed_region`, `configure(parameters) -> None`

4. **Concrete Strategy Implementations**:
   - **BinaryProcessingStrategy**: Processes binary regions with appropriate threshold and no dithering.
   - **GrayscaleProcessingStrategy**: Processes grayscale regions with dithering and appropriate parameters.

### 2.3 Configuration Management

The Configuration Management component is responsible for loading, validating, and providing access to configuration parameters.

#### 2.3.1 Class Diagram

```
┌───────────────────────────┐
│   ConfigurationManager    │
├───────────────────────────┤
│ - config                  │
│ - validators              │
├───────────────────────────┤
│ + load_config()           │
│ + validate_config()       │
│ + get_config()            │
│ + set_config()            │
└───────────────────────────┘
```

#### 2.3.2 Key Components

1. **ConfigurationManager**: Singleton responsible for managing configuration.
   - Responsibilities: Load and validate configuration, provide access to configuration parameters.
   - Interface: `load_config(file_path) -> None`, `validate_config() -> bool`, `get_config() -> Dict`

### 2.4 User Interface Components

Optional user interface components for region refinement and parameter adjustment.

#### 2.4.1 Class Diagram

```
┌───────────────────────────┐
│   UserInterfaceManager    │
├───────────────────────────┤
│ - observers               │
├───────────────────────────┤
│ + display_regions()       │
│ + update_regions()        │
│ + adjust_parameters()     │
└───────────────────────────┘
```

#### 2.4.2 Key Components

1. **UserInterfaceManager**: Manages user interaction for region refinement and parameter adjustment.
   - Responsibilities: Display detected regions, handle user adjustments, update processing parameters.
   - Interface: `display_regions(image, region_mask) -> None`, `update_regions(region_updates) -> region_mask`

## 3. Interface & API Design

### 3.1 Detection Strategy Interface

```python
from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any, Optional

class DetectionStrategy(ABC):
    """
    Interface for all region detection strategies.
    """
    
    @abstractmethod
    def analyze(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze the image to identify binary and grayscale regions.
        
        Args:
            image: The input image to analyze (numpy array).
            
        Returns:
            A probability map where each pixel's value represents the likelihood
            of belonging to a grayscale region (0 = binary, 1 = grayscale).
        """
        pass
    
    @abstractmethod
    def configure(self, parameters: Dict[str, Any]) -> None:
        """
        Configure the detection strategy with specific parameters.
        
        Args:
            parameters: Dictionary of configuration parameters.
        """
        pass
```

### 3.2 Processing Strategy Interface

```python
from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any

class ProcessingStrategy(ABC):
    """
    Interface for all region processing strategies.
    """
    
    @abstractmethod
    def process(self, image: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
        """
        Process regions of an image according to the strategy.
        
        Args:
            image: The input image to process.
            region_mask: Mask indicating the regions to process (1 = process, 0 = ignore).
            
        Returns:
            The processed image regions.
        """
        pass
    
    @abstractmethod
    def configure(self, parameters: Dict[str, Any]) -> None:
        """
        Configure the processing strategy with specific parameters.
        
        Args:
            parameters: Dictionary of configuration parameters.
        """
        pass
```

### 3.3 Region Component Interface

```python
from abc import ABC, abstractmethod
import numpy as np

class RegionComponent(ABC):
    """
    Interface for region components (Composite Pattern).
    """
    
    @abstractmethod
    def get_mask(self) -> np.ndarray:
        """
        Get the mask representing the region.
        
        Returns:
            A binary mask where 1 indicates the region and 0 indicates background.
        """
        pass
    
    @abstractmethod
    def get_bounding_box(self) -> tuple:
        """
        Get the bounding box coordinates of the region.
        
        Returns:
            Tuple of (x_min, y_min, x_max, y_max).
        """
        pass
```

### 3.4 Data Models

#### 3.4.1 Region Model

```python
class Region:
    """
    Represents a detected region in an image.
    """
    
    def __init__(self, mask: np.ndarray, region_type: str, confidence: float = 1.0):
        """
        Initialize a region.
        
        Args:
            mask: Binary mask representing the region.
            region_type: Type of region ('binary' or 'grayscale').
            confidence: Confidence score for the detection (0-1).
        """
        self.mask = mask
        self.region_type = region_type
        self.confidence = confidence
        self.bounding_box = self._compute_bounding_box()
    
    def _compute_bounding_box(self) -> tuple:
        """Compute the bounding box of the region."""
        # Implementation details
        pass
    
    def expand(self, pixels: int) -> None:
        """
        Expand the region by a specified number of pixels.
        
        Args:
            pixels: Number of pixels to expand the region by.
        """
        # Implementation details
        pass
```

#### 3.4.2 Configuration Model

```python
class Configuration:
    """
    Configuration model for the Greyscale Binary Separator.
    """
    
    def __init__(self):
        """Initialize default configuration."""
        self.detection_strategies = []
        self.binary_threshold = 128
        self.grayscale_dpi = 300
        self.dither_type = "floyd-steinberg"
        self.region_expansion = 5
        self.brightness_adjustment = 0
        self.contrast_adjustment = 0
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if the configuration is valid, False otherwise.
        """
        # Implementation details
        pass
```

### 3.5 Exception Handling Strategy

The system will use a layered exception handling approach:

1. **Low-level exceptions**: Caught and wrapped in domain-specific exceptions.
2. **Domain-specific exceptions**: Propagated to the application layer.
3. **Application layer**: Handles exceptions, logs errors, and provides appropriate feedback.
4. **Presentation layer**: Displays user-friendly error messages.

```python
class GreyscaleBinarySeparatorError(Exception):
    """Base exception for all Greyscale Binary Separator errors."""
    pass

class RegionDetectionError(GreyscaleBinarySeparatorError):
    """Error during region detection."""
    pass

class RegionProcessingError(GreyscaleBinarySeparatorError):
    """Error during region processing."""
    pass

class ConfigurationError(GreyscaleBinarySeparatorError):
    """Error in configuration parameters."""
    pass
```

## 4. Implementation Strategy

### 4.1 High-Level Roadmap

1. **Foundation Phase**
   - Implement core interfaces and abstract classes
   - Set up configuration management
   - Create basic pipeline structure

2. **Detection Phase**
   - Implement histogram analysis strategy
   - Implement texture analysis strategy
   - Implement edge detection strategy
   - Integrate and test detection pipeline

3. **Processing Phase**
   - Implement binary processing strategy
   - Implement grayscale processing strategy
   - Integrate and test processing pipeline

4. **Integration Phase**
   - Integrate detection and processing engines
   - Implement region expansion and cleanup
   - Implement region merging

5. **Refinement Phase**
   - Optimize performance
   - Add user interaction capabilities
   - Enhance error handling and logging

### 4.2 Component-Specific Implementation Plans

#### 4.2.1 Region Detection Engine

1. **Implement DetectionStrategy Interface**
   - Define abstract methods
   - Create base class with common functionality

2. **Implement Histogram Analysis Strategy**
   - Implement multi-scale histogram analysis
   - Add configurable parameters
   - Optimize for performance

3. **Implement Texture Analysis Strategy**
   - Implement LBP and GLCM features
   - Create hybrid approach
   - Optimize for performance

4. **Implement Edge Detection Strategy**
   - Implement multi-scale edge detection
   - Add configurable parameters
   - Optimize for performance

5. **Implement Strategy Provider**
   - Create factory for strategies
   - Implement strategy registration
   - Add configuration support

6. **Integrate Detection Pipeline**
   - Implement pipeline coordination
   - Add result combination logic
   - Implement post-processing

#### 4.2.2 Region Processing Engine

1. **Implement ProcessingStrategy Interface**
   - Define abstract methods
   - Create base class with common functionality

2. **Implement Binary Processing Strategy**
   - Implement thresholding
   - Add cleanup operations
   - Optimize for performance

3. **Implement Grayscale Processing Strategy**
   - Implement brightness/contrast adjustment
   - Implement dithering with configurable parameters
   - Optimize for performance

4. **Implement Strategy Provider**
   - Create factory for strategies
   - Implement strategy registration
   - Add configuration support

5. **Integrate Processing Pipeline**
   - Implement pipeline coordination
   - Add region merging logic
   - Implement post-processing

### 4.3 Testing Strategy

1. **Unit Testing**
   - Test each strategy and component in isolation
   - Use mock objects for dependencies
   - Achieve 95%+ code coverage

2. **Integration Testing**
   - Test detection and processing pipelines
   - Test different configuration scenarios
   - Verify correct behavior for edge cases

3. **Performance Testing**
   - Measure processing time for various image sizes
   - Identify bottlenecks
   - Optimize critical paths

4. **Acceptance Testing**
   - Verify results against manually processed images
   - Test with real-world documents
   - Validate user interaction flows

### 4.4 Risk Mitigation Strategy

1. **Technical Risks**
   - **Accuracy of detection**: Mitigate with hybrid approach, user verification.
   - **Performance issues**: Profile early, optimize hotspots, implement early termination.
   - **Memory consumption**: Use efficient data structures, implement progressive processing.

2. **Integration Risks**
   - **Compatibility with existing system**: Follow established patterns, use adapters if needed.
   - **Configuration complexity**: Provide sensible defaults, validate configurations.

3. **User Experience Risks**
   - **Usability of manual adjustments**: Design intuitive UI, provide previews.
   - **Parameter tuning complexity**: Hide complexity behind sensible defaults, use presets.

## 5. Performance Considerations

1. **Computational Efficiency**
   - Use optimized image processing libraries (OpenCV, scikit-image)
   - Implement multi-resolution approach for initial detection
   - Use early termination for clear cases

2. **Memory Efficiency**
   - Avoid redundant copies of image data
   - Process in tiles for large images
   - Use sparse representations where appropriate

3. **Parallelization**
   - Parallelize window processing in detection strategies
   - Process independent regions concurrently
   - Utilize hardware acceleration where available

## 6. Extension Points

The architecture includes several well-defined extension points:

1. **New Detection Strategies**
   - Implement the DetectionStrategy interface
   - Register with the strategy provider

2. **New Processing Strategies**
   - Implement the ProcessingStrategy interface
   - Register with the strategy provider

3. **Enhanced Region Representations**
   - Extend the Region class
   - Implement new region component types

4. **User Interaction Enhancements**
   - Implement the Observer pattern for UI updates
   - Add new Command implementations for user actions

5. **Pipeline Extensions**
   - Add new pipeline stages
   - Implement custom result combination logic

## 7. Integration with Existing System

The Greyscale Binary Separator will integrate with the existing BatchImageProcessor system:

1. **Processor Implementation**
   - Implement as a new processor class in the processors/image directory
   - Follow existing processor interface pattern

2. **Factory Integration**
   - Add to ImageProcessorFactory for creation
   - Support configuration through YAML files

3. **Pipeline Compatibility**
   - Ensure compatibility with existing image pipeline
   - Support batch processing workflow

4. **Configuration Structure**
   - Follow existing configuration patterns
   - Provide example configuration files

## 8. Conclusion

The Greyscale Binary Separator architecture provides a robust, flexible, and maintainable solution to the problem of detecting and separately processing grayscale and binary regions in document images. By adhering to SOLID principles and applying appropriate design patterns, the system achieves a high degree of extensibility and maintainability while providing effective functionality.

The multi-stage hybrid approach to detection, combined with the pipeline architecture for processing, offers the best balance of accuracy, flexibility, and performance based on our comprehensive analysis of alternatives. The use of polymorphic interfaces throughout the system enhances its ability to adapt to future requirements and integrate smoothly with the existing BatchImageProcessor system.