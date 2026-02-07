"""
WellNest Health Integrations Module

Provides integration bridges for Apple HealthKit and Google Fit.
Note: Actual HealthKit integration requires iOS native code.
      This module provides the backend API structure for receiving and processing health data.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json


class HealthDataType(str, Enum):
    """Types of health data that can be synced."""
    STEPS = "steps"
    WEIGHT = "weight"
    HEART_RATE = "heart_rate"
    RESTING_HEART_RATE = "resting_heart_rate"
    HRV = "hrv"
    SLEEP = "sleep"
    ACTIVE_CALORIES = "active_calories"
    WORKOUT = "workout"
    DISTANCE = "distance"
    FLOORS_CLIMBED = "floors_climbed"
    BLOOD_OXYGEN = "blood_oxygen"


@dataclass
class HealthDataPoint:
    """A single health data point."""
    data_type: HealthDataType
    value: float
    unit: str
    timestamp: datetime
    source: str  # 'apple_healthkit', 'google_fit', 'manual'
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SleepData:
    """Sleep data structure."""
    start_time: datetime
    end_time: datetime
    total_hours: float
    deep_sleep_hours: float
    light_sleep_hours: float
    rem_sleep_hours: float
    awake_hours: float
    sleep_score: Optional[int] = None  # 0-100


@dataclass
class WorkoutData:
    """Workout data structure."""
    workout_type: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    calories_burned: int
    distance_km: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None


@dataclass
class DailyHealthSummary:
    """Daily health summary from integrations."""
    date: date
    steps: int
    distance_km: float
    active_calories: int
    floors_climbed: int
    sleep_hours: Optional[float]
    sleep_score: Optional[int]
    avg_heart_rate: Optional[int]
    resting_heart_rate: Optional[int]
    hrv_ms: Optional[int]
    workouts: List[WorkoutData]


class HealthKitService:
    """
    Service for processing Apple HealthKit data.

    Note: This service receives data from the iOS app via API calls.
    The actual HealthKit queries happen on the device.
    """

    # Mapping of HealthKit types to our internal types
    HEALTHKIT_TYPE_MAP = {
        "HKQuantityTypeIdentifierStepCount": HealthDataType.STEPS,
        "HKQuantityTypeIdentifierBodyMass": HealthDataType.WEIGHT,
        "HKQuantityTypeIdentifierHeartRate": HealthDataType.HEART_RATE,
        "HKQuantityTypeIdentifierRestingHeartRate": HealthDataType.RESTING_HEART_RATE,
        "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": HealthDataType.HRV,
        "HKQuantityTypeIdentifierActiveEnergyBurned": HealthDataType.ACTIVE_CALORIES,
        "HKQuantityTypeIdentifierDistanceWalkingRunning": HealthDataType.DISTANCE,
        "HKQuantityTypeIdentifierFlightsClimbed": HealthDataType.FLOORS_CLIMBED,
        "HKQuantityTypeIdentifierOxygenSaturation": HealthDataType.BLOOD_OXYGEN,
        "HKCategoryTypeIdentifierSleepAnalysis": HealthDataType.SLEEP,
    }

    @staticmethod
    def parse_healthkit_data(raw_data: Dict[str, Any]) -> List[HealthDataPoint]:
        """
        Parse raw HealthKit data from iOS app.

        Expected format:
        {
            "type": "HKQuantityTypeIdentifierStepCount",
            "samples": [
                {
                    "value": 1234,
                    "unit": "count",
                    "startDate": "2024-01-15T10:00:00Z",
                    "endDate": "2024-01-15T11:00:00Z"
                }
            ]
        }
        """
        data_points = []
        hk_type = raw_data.get("type")
        internal_type = HealthKitService.HEALTHKIT_TYPE_MAP.get(hk_type)

        if not internal_type:
            return data_points

        for sample in raw_data.get("samples", []):
            try:
                timestamp = datetime.fromisoformat(
                    sample["startDate"].replace("Z", "+00:00")
                )
                data_points.append(HealthDataPoint(
                    data_type=internal_type,
                    value=float(sample["value"]),
                    unit=sample.get("unit", ""),
                    timestamp=timestamp,
                    source="apple_healthkit",
                    metadata={
                        "endDate": sample.get("endDate"),
                        "sourceName": sample.get("sourceName"),
                    }
                ))
            except (KeyError, ValueError):
                continue

        return data_points

    @staticmethod
    def parse_sleep_data(raw_data: Dict[str, Any]) -> Optional[SleepData]:
        """
        Parse HealthKit sleep analysis data.

        Expected format:
        {
            "sleepSamples": [
                {
                    "value": "HKCategoryValueSleepAnalysisInBed|Asleep|...",
                    "startDate": "2024-01-15T22:00:00Z",
                    "endDate": "2024-01-16T06:00:00Z"
                }
            ]
        }
        """
        samples = raw_data.get("sleepSamples", [])
        if not samples:
            return None

        # Calculate sleep stages
        in_bed_minutes = 0
        asleep_minutes = 0
        deep_sleep_minutes = 0
        rem_sleep_minutes = 0
        awake_minutes = 0

        start_time = None
        end_time = None

        for sample in samples:
            try:
                sample_start = datetime.fromisoformat(
                    sample["startDate"].replace("Z", "+00:00")
                )
                sample_end = datetime.fromisoformat(
                    sample["endDate"].replace("Z", "+00:00")
                )
                duration = (sample_end - sample_start).total_seconds() / 60

                if start_time is None or sample_start < start_time:
                    start_time = sample_start
                if end_time is None or sample_end > end_time:
                    end_time = sample_end

                value = sample.get("value", "")
                if "InBed" in value:
                    in_bed_minutes += duration
                elif "Asleep" in value or "AsleepCore" in value:
                    asleep_minutes += duration
                elif "AsleepDeep" in value:
                    deep_sleep_minutes += duration
                elif "AsleepREM" in value:
                    rem_sleep_minutes += duration
                elif "Awake" in value:
                    awake_minutes += duration

            except (KeyError, ValueError):
                continue

        if start_time is None or end_time is None:
            return None

        total_hours = (deep_sleep_minutes + asleep_minutes + rem_sleep_minutes) / 60

        return SleepData(
            start_time=start_time,
            end_time=end_time,
            total_hours=round(total_hours, 2),
            deep_sleep_hours=round(deep_sleep_minutes / 60, 2),
            light_sleep_hours=round(asleep_minutes / 60, 2),
            rem_sleep_hours=round(rem_sleep_minutes / 60, 2),
            awake_hours=round(awake_minutes / 60, 2),
        )

    @staticmethod
    def parse_workout_data(raw_data: Dict[str, Any]) -> Optional[WorkoutData]:
        """
        Parse HealthKit workout data.

        Expected format:
        {
            "workoutActivityType": "HKWorkoutActivityTypeRunning",
            "startDate": "2024-01-15T07:00:00Z",
            "endDate": "2024-01-15T07:45:00Z",
            "duration": 2700,
            "totalEnergyBurned": 350,
            "totalDistance": 5.5
        }
        """
        try:
            workout_type = raw_data.get("workoutActivityType", "")
            # Clean up HealthKit type name
            workout_type = workout_type.replace("HKWorkoutActivityType", "").lower()

            start_time = datetime.fromisoformat(
                raw_data["startDate"].replace("Z", "+00:00")
            )
            end_time = datetime.fromisoformat(
                raw_data["endDate"].replace("Z", "+00:00")
            )
            duration = int(raw_data.get("duration", 0) / 60)

            return WorkoutData(
                workout_type=workout_type,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration,
                calories_burned=int(raw_data.get("totalEnergyBurned", 0)),
                distance_km=raw_data.get("totalDistance"),
                avg_heart_rate=raw_data.get("averageHeartRate"),
                max_heart_rate=raw_data.get("maxHeartRate"),
            )
        except (KeyError, ValueError):
            return None


class GoogleFitService:
    """
    Service for processing Google Fit data.

    Note: This service receives data from the Android app via API calls.
    The actual Google Fit queries happen on the device.
    """

    # Mapping of Google Fit data types to our internal types
    GOOGLE_FIT_TYPE_MAP = {
        "com.google.step_count.delta": HealthDataType.STEPS,
        "com.google.weight": HealthDataType.WEIGHT,
        "com.google.heart_rate.bpm": HealthDataType.HEART_RATE,
        "com.google.calories.expended": HealthDataType.ACTIVE_CALORIES,
        "com.google.distance.delta": HealthDataType.DISTANCE,
        "com.google.sleep.segment": HealthDataType.SLEEP,
    }

    @staticmethod
    def parse_google_fit_data(raw_data: Dict[str, Any]) -> List[HealthDataPoint]:
        """
        Parse raw Google Fit data from Android app.

        Expected format:
        {
            "dataType": "com.google.step_count.delta",
            "dataPoints": [
                {
                    "value": 1234,
                    "startTimeNanos": 1705320000000000000,
                    "endTimeNanos": 1705323600000000000
                }
            ]
        }
        """
        data_points = []
        gf_type = raw_data.get("dataType")
        internal_type = GoogleFitService.GOOGLE_FIT_TYPE_MAP.get(gf_type)

        if not internal_type:
            return data_points

        for point in raw_data.get("dataPoints", []):
            try:
                # Convert nanos to datetime
                start_nanos = point.get("startTimeNanos", 0)
                timestamp = datetime.fromtimestamp(start_nanos / 1e9)

                # Get value (could be in different fields)
                value = point.get("value")
                if isinstance(value, list) and len(value) > 0:
                    value = value[0].get("fpVal") or value[0].get("intVal", 0)
                elif isinstance(value, dict):
                    value = value.get("fpVal") or value.get("intVal", 0)

                data_points.append(HealthDataPoint(
                    data_type=internal_type,
                    value=float(value) if value else 0,
                    unit=point.get("unit", ""),
                    timestamp=timestamp,
                    source="google_fit",
                    metadata={
                        "endTimeNanos": point.get("endTimeNanos"),
                        "dataSourceId": point.get("dataSourceId"),
                    }
                ))
            except (KeyError, ValueError, TypeError):
                continue

        return data_points

    @staticmethod
    def parse_sleep_data(raw_data: Dict[str, Any]) -> Optional[SleepData]:
        """
        Parse Google Fit sleep segment data.

        Sleep stage types:
        1 = Awake
        2 = Sleep
        3 = Out of bed
        4 = Light sleep
        5 = Deep sleep
        6 = REM
        """
        segments = raw_data.get("sleepSegments", [])
        if not segments:
            return None

        deep_sleep_minutes = 0
        light_sleep_minutes = 0
        rem_sleep_minutes = 0
        awake_minutes = 0

        start_time = None
        end_time = None

        for segment in segments:
            try:
                seg_start = datetime.fromtimestamp(
                    segment["startTimeNanos"] / 1e9
                )
                seg_end = datetime.fromtimestamp(
                    segment["endTimeNanos"] / 1e9
                )
                duration = (seg_end - seg_start).total_seconds() / 60

                if start_time is None or seg_start < start_time:
                    start_time = seg_start
                if end_time is None or seg_end > end_time:
                    end_time = seg_end

                sleep_type = segment.get("sleepSegmentType", 2)
                if sleep_type == 1:
                    awake_minutes += duration
                elif sleep_type in [2, 4]:
                    light_sleep_minutes += duration
                elif sleep_type == 5:
                    deep_sleep_minutes += duration
                elif sleep_type == 6:
                    rem_sleep_minutes += duration

            except (KeyError, ValueError):
                continue

        if start_time is None or end_time is None:
            return None

        total_hours = (deep_sleep_minutes + light_sleep_minutes + rem_sleep_minutes) / 60

        return SleepData(
            start_time=start_time,
            end_time=end_time,
            total_hours=round(total_hours, 2),
            deep_sleep_hours=round(deep_sleep_minutes / 60, 2),
            light_sleep_hours=round(light_sleep_minutes / 60, 2),
            rem_sleep_hours=round(rem_sleep_minutes / 60, 2),
            awake_hours=round(awake_minutes / 60, 2),
        )


def aggregate_daily_health_data(
    data_points: List[HealthDataPoint],
    sleep_data: Optional[SleepData] = None,
    workouts: Optional[List[WorkoutData]] = None,
    target_date: Optional[date] = None
) -> DailyHealthSummary:
    """
    Aggregate health data points into a daily summary.

    Args:
        data_points: List of health data points
        sleep_data: Optional sleep data
        workouts: Optional list of workouts
        target_date: Date to aggregate for (defaults to today)

    Returns:
        DailyHealthSummary with aggregated data
    """
    target_date = target_date or date.today()

    # Filter data points for target date
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    filtered_points = [
        p for p in data_points
        if day_start <= p.timestamp < day_end
    ]

    # Aggregate by type
    steps = sum(
        p.value for p in filtered_points
        if p.data_type == HealthDataType.STEPS
    )

    distance = sum(
        p.value for p in filtered_points
        if p.data_type == HealthDataType.DISTANCE
    )

    active_calories = sum(
        p.value for p in filtered_points
        if p.data_type == HealthDataType.ACTIVE_CALORIES
    )

    floors = sum(
        p.value for p in filtered_points
        if p.data_type == HealthDataType.FLOORS_CLIMBED
    )

    # Heart rate - average of all readings
    hr_readings = [
        p.value for p in filtered_points
        if p.data_type == HealthDataType.HEART_RATE
    ]
    avg_hr = int(sum(hr_readings) / len(hr_readings)) if hr_readings else None

    # Resting heart rate - take the lowest reading or specific resting HR
    resting_hr_readings = [
        p.value for p in filtered_points
        if p.data_type == HealthDataType.RESTING_HEART_RATE
    ]
    resting_hr = int(min(resting_hr_readings)) if resting_hr_readings else None

    # HRV - average
    hrv_readings = [
        p.value for p in filtered_points
        if p.data_type == HealthDataType.HRV
    ]
    hrv = int(sum(hrv_readings) / len(hrv_readings)) if hrv_readings else None

    return DailyHealthSummary(
        date=target_date,
        steps=int(steps),
        distance_km=round(distance / 1000, 2) if distance > 100 else round(distance, 2),
        active_calories=int(active_calories),
        floors_climbed=int(floors),
        sleep_hours=sleep_data.total_hours if sleep_data else None,
        sleep_score=sleep_data.sleep_score if sleep_data else None,
        avg_heart_rate=avg_hr,
        resting_heart_rate=resting_hr,
        hrv_ms=hrv,
        workouts=workouts or [],
    )
