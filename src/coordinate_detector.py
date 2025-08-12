"""
Coordinate detection module using OpenCV and MediaPipe for logo placement
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, Dict, List
import mediapipe as mp

logger = logging.getLogger(__name__)


class CoordinateDetector:
    """Detects optimal coordinates for logo placement using OpenCV and MediaPipe"""
    
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize pose detection
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
        # Initialize hand detection
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        
        # Initialize face detection
        self.face_detection = self.mp_face.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )
    
    def detect_placement_coordinates(self, image_path: str, logo_path: str, 
                                   decoration_location: str, location_as_per_word: str) -> Optional[Dict]:
        """
        Detect optimal coordinates for logo placement
        
        Args:
            image_path: Path to the product image
            logo_path: Path to the logo image
            decoration_location: Location specification from Excel
            location_as_per_word: Word-based location description
            
        Returns:
            Dictionary containing x, y coordinates and dimensions
        """
        try:
            # Load images
            image = cv2.imread(image_path)
            logo = cv2.imread(logo_path)
            
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return None
            
            if logo is None:
                logger.error(f"Could not load logo: {logo_path}")
                return None
            
            # Get image dimensions
            img_height, img_width = image.shape[:2]
            logo_height, logo_width = logo.shape[:2]
            
            # Detect features in the image
            features = self._detect_features(image)
            
            # Determine optimal placement based on location specifications
            coordinates = self._calculate_optimal_placement(
                image, logo, features, decoration_location, location_as_per_word
            )
            
            if coordinates:
                logger.info(f"Detected coordinates: {coordinates}")
                return coordinates
            else:
                # Fallback to default placement
                return self._get_default_placement(img_width, img_height, logo_width, logo_height)
            
        except Exception as e:
            logger.error(f"Error detecting coordinates: {e}")
            return None
    
    def _detect_features(self, image: np.ndarray) -> Dict:
        """
        Detect features in the image using MediaPipe
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary containing detected features
        """
        features = {
            'pose': None,
            'hands': [],
            'faces': [],
            'edges': None,
            'corners': [],
            'contours': []
        }
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect pose
            pose_results = self.pose.process(rgb_image)
            if pose_results.pose_landmarks:
                features['pose'] = pose_results.pose_landmarks
                logger.info("Pose detected in image")
            
            # Detect hands
            hand_results = self.hands.process(rgb_image)
            if hand_results.multi_hand_landmarks:
                features['hands'] = hand_results.multi_hand_landmarks
                logger.info(f"Detected {len(hand_results.multi_hand_landmarks)} hands")
            
            # Detect faces
            face_results = self.face_detection.process(rgb_image)
            if face_results.detections:
                features['faces'] = face_results.detections
                logger.info(f"Detected {len(face_results.detections)} faces")
            
            # Detect edges and corners
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            features['edges'] = edges
            
            # Detect corners
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            if corners is not None:
                features['corners'] = corners
            
            # Detect contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features['contours'] = contours
            
        except Exception as e:
            logger.error(f"Error detecting features: {e}")
        
        return features
    
    def _calculate_optimal_placement(self, image: np.ndarray, logo: np.ndarray, 
                                   features: Dict, decoration_location: str, 
                                   location_as_per_word: str) -> Optional[Dict]:
        """
        Calculate optimal logo placement based on detected features and location specifications
        
        Args:
            image: Product image
            logo: Logo image
            features: Detected features dictionary
            decoration_location: Location from Excel
            location_as_per_word: Word description of location
            
        Returns:
            Coordinates dictionary or None
        """
        try:
            img_height, img_width = image.shape[:2]
            logo_height, logo_width = logo.shape[:2]
            
            # Parse location specifications
            location_lower = decoration_location.lower() if decoration_location else ""
            word_location_lower = location_as_per_word.lower() if location_as_per_word else ""
            
            # Determine placement strategy based on location
            if any(word in location_lower or word in word_location_lower 
                   for word in ['chest', 'front', 'center']):
                return self._place_on_chest(image, logo, features)
            
            elif any(word in location_lower or word in word_location_lower 
                     for word in ['sleeve', 'arm']):
                return self._place_on_sleeve(image, logo, features)
            
            elif any(word in location_lower or word in word_location_lower 
                     for word in ['back']):
                return self._place_on_back(image, logo, features)
            
            elif any(word in location_lower or word in word_location_lower 
                     for word in ['collar', 'neck']):
                return self._place_on_collar(image, logo, features)
            
            elif any(word in location_lower or word in word_location_lower 
                     for word in ['pocket']):
                return self._place_on_pocket(image, logo, features)
            
            else:
                # Default placement strategy
                return self._smart_placement(image, logo, features)
            
        except Exception as e:
            logger.error(f"Error calculating optimal placement: {e}")
            return None
    
    def _place_on_chest(self, image: np.ndarray, logo: np.ndarray, features: Dict) -> Dict:
        """Place logo on chest area"""
        img_height, img_width = image.shape[:2]
        logo_height, logo_width = logo.shape[:2]
        
        if features['pose']:
            # Use pose landmarks to find chest area
            landmarks = features['pose'].landmark
            
            # Get shoulder landmarks
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            # Calculate chest center
            chest_x = int((left_shoulder.x + right_shoulder.x) / 2 * img_width)
            chest_y = int((left_shoulder.y + 0.3) * img_height)  # Slightly below shoulders
            
            # Adjust for logo size
            x = max(0, min(chest_x - logo_width // 2, img_width - logo_width))
            y = max(0, min(chest_y, img_height - logo_height))
            
        else:
            # Fallback: center-upper area
            x = (img_width - logo_width) // 2
            y = img_height // 4
        
        return {
            'x': x,
            'y': y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'chest'
        }
    
    def _place_on_sleeve(self, image: np.ndarray, logo: np.ndarray, features: Dict) -> Dict:
        """Place logo on sleeve area"""
        img_height, img_width = image.shape[:2]
        logo_height, logo_width = logo.shape[:2]
        
        if features['pose']:
            landmarks = features['pose'].landmark
            
            # Get arm landmarks
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW]
            
            # Place on upper arm
            x = int(left_shoulder.x * img_width) - logo_width
            y = int((left_shoulder.y + left_elbow.y) / 2 * img_height)
            
            # Ensure within bounds
            x = max(0, min(x, img_width - logo_width))
            y = max(0, min(y, img_height - logo_height))
        else:
            # Fallback: left side
            x = img_width // 8
            y = img_height // 3
        
        return {
            'x': x,
            'y': y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'sleeve'
        }
    
    def _place_on_back(self, image: np.ndarray, logo: np.ndarray, features: Dict) -> Dict:
        """Place logo on back area"""
        img_height, img_width = image.shape[:2]
        logo_height, logo_width = logo.shape[:2]
        
        # Center of upper back area
        x = (img_width - logo_width) // 2
        y = img_height // 6
        
        return {
            'x': x,
            'y': y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'back'
        }
    
    def _place_on_collar(self, image: np.ndarray, logo: np.ndarray, features: Dict) -> Dict:
        """Place logo on collar area"""
        img_height, img_width = image.shape[:2]
        logo_height, logo_width = logo.shape[:2]
        
        # Upper center area
        x = (img_width - logo_width) // 2
        y = img_height // 20
        
        return {
            'x': x,
            'y': y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'collar'
        }
    
    def _place_on_pocket(self, image: np.ndarray, logo: np.ndarray, features: Dict) -> Dict:
        """Place logo on pocket area"""
        img_height, img_width = image.shape[:2]
        logo_height, logo_width = logo.shape[:2]
        
        # Left chest pocket area
        x = img_width // 6
        y = img_height // 3
        
        return {
            'x': x,
            'y': y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'pocket'
        }
    
    def _smart_placement(self, image: np.ndarray, logo: np.ndarray, features: Dict) -> Dict:
        """Smart placement based on available space and features"""
        img_height, img_width = image.shape[:2]
        logo_height, logo_width = logo.shape[:2]
        
        # Find areas with least visual complexity
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Divide image into grid and find least complex area
        grid_size = 8
        cell_width = img_width // grid_size
        cell_height = img_height // grid_size
        
        min_complexity = float('inf')
        best_x, best_y = img_width // 2, img_height // 2
        
        for i in range(grid_size - 2):  # Leave margin
            for j in range(grid_size - 2):
                x_start = i * cell_width
                y_start = j * cell_height
                
                # Check if logo fits
                if x_start + logo_width > img_width or y_start + logo_height > img_height:
                    continue
                
                # Calculate complexity (variance in grayscale)
                roi = gray[y_start:y_start + cell_height, x_start:x_start + cell_width]
                complexity = np.var(roi)
                
                if complexity < min_complexity:
                    min_complexity = complexity
                    best_x = x_start
                    best_y = y_start
        
        return {
            'x': best_x,
            'y': best_y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'smart'
        }
    
    def _get_default_placement(self, img_width: int, img_height: int, 
                             logo_width: int, logo_height: int) -> Dict:
        """Get default placement when detection fails"""
        x = (img_width - logo_width) // 2
        y = img_height // 4
        
        return {
            'x': x,
            'y': y,
            'width': logo_width,
            'height': logo_height,
            'placement_type': 'default'
        }