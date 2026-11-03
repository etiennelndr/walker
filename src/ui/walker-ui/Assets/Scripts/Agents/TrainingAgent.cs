using System;
using System.Collections.Generic;
using System.Linq;

using Api;
using Api.Models;

using UnityEngine;
using UnityEngine.AI;

using Object = UnityEngine.Object;
using Random = System.Random;
using Vector3 = UnityEngine.Vector3;

namespace Agents {
    [Serializable]
    public class TargetPointsConfig {
        [Tooltip("Whether the target points are drawn in the Scene view")]
        public bool isVisible;

        [Min(0.5f)]
        [Tooltip("Height of the line drawn at each target point, in Unity units")]
        public float height = 2.5f;
    }

    [Serializable]
    public class TrainingAgentConfig : BaseAgentConfig {
        [Tooltip("Settings of the drawing of the target points")]
        public TargetPointsConfig targetPoints;

        [Min(0.5f)]
        [Tooltip("Distance to the current target at which the walker picks the next one")]
        public float remainingDistanceTolerance = 2f;

        [Range(0, 180)]
        [Tooltip("Largest turn at a target, in degrees, beyond which the walker turns back")]
        public int maxTurnAngle = 135;
    }

    public class TrainingAgent : BaseAgent<TrainingAgentConfig> {
        private readonly NavMeshAgent _navMeshAgent;

        // Own generator, so that the draws of a walker do not depend on the other ones
        private readonly Random _rnd;

        private readonly TargetPoints _targetPoints;

        private Vector3 _currentTargetPoint;

        // Direction in which the agent enters its current target, or zero if unknown (e.g. for its
        // first target)
        private Vector3 _incomingDirection;
        private bool _isSendingRecord;
        private List<Vector3> _nextTargetPoints;
        private Vector3 _previousTargetPoint;

        public TrainingAgent(TrainingAgentConfig config, Walker walker) : base(config, walker) {
            _navMeshAgent = walker.GetComponent<NavMeshAgent>();
            _targetPoints = Object.FindAnyObjectByType<TargetPoints>();

            _rnd = new Random(UnityEngine.Random.Range(1, int.MaxValue));
        }

        protected override Vector3 Velocity => _navMeshAgent.velocity;

        public override void Init() {
            // Disabling auto-braking allows for continuous movement between points (i.e., the agent
            // doesn't slow down as it approaches a destination point).
            _navMeshAgent.autoBraking = false;
            // Disabling obstacle avoidance lets walkers pass through each other, since their rays
            // ignore them. Other walkers thus never change the trajectory of a walker.
            _navMeshAgent.obstacleAvoidanceType = ObstacleAvoidanceType.NoObstacleAvoidance;

            // Without it, the records would lack the seed of the map
            if (mapGenerator == null) {
                Disable("A MapGenerator component must be added to the scene");
                return;
            }

            if (_targetPoints == null) {
                Disable("A TargetPoints component must be added to the scene");
                return;
            }

            if (_targetPoints.Positions.Count() < 2) {
                Disable(
                    "At least two target points must be added as children of" +
                    $" '{_targetPoints.name}'"
                );
                return;
            }

            // Start from a random target point, which lies on a street and thus on the NavMesh
            Vector3 startPoint =
                _targetPoints.Positions.ElementAt(_rnd.Next(0, _targetPoints.Positions.Count()));
            walker.transform.position = startPoint;

            // Enable the agent only on its start point, so that it attaches to the NavMesh there
            _navMeshAgent.enabled = true;
            if (!_navMeshAgent.isOnNavMesh) {
                Disable($"Could not move the walker to its start point {startPoint}");
                return;
            }

            // Without any incoming direction, the first target may be in any direction
            _currentTargetPoint = startPoint;
            _previousTargetPoint = _currentTargetPoint;
            UpdateTarget();
        }

        public override void Step() {
            // Choose the next destination point when the agent gets close to the current one
            if (!_navMeshAgent.pathPending &&
                _navMeshAgent.remainingDistance < config.remainingDistanceTolerance) {
                UpdateTarget();
            }

            if (config.targetPoints.isVisible) {
                DrawTargetPoints();
            }

            if (Time.frameCount % config.rays.sendEveryNFrames == 0) {
                SendRecord();
            }
        }

        protected override void Enable(string reason) {
            base.Enable(reason);

            if (_navMeshAgent.isOnNavMesh) {
                _navMeshAgent.isStopped = false;
            }
        }

        protected override void Disable(string reason) {
            base.Disable(reason);

            if (_navMeshAgent.isOnNavMesh) {
                _navMeshAgent.isStopped = true;
            }
        }

        protected override Record CollectRecord() {
            Record record = base.CollectRecord();
            record.desiredVelocity = _navMeshAgent.desiredVelocity;
            record.target = _currentTargetPoint;
            return record;
        }

        private async void SendRecord() {
            if (_isSendingRecord) {
                return;
            }

            try {
                Record record = CollectRecord();
                _isSendingRecord = true;
                await apiClient.CreateRecord(record);
            }
            catch (ApiException e) {
                Disable(e.Message);
            }
            catch (Exception e) {
                Disable($"Unexpected error while sending the record: {e.Message}");
            }
            finally {
                _isSendingRecord = false;
            }
        }

        private void UpdateTarget() {
            // Retrieve the points the agent may go to from its current target
            List<Vector3> candidatePoints = GetCandidatePoints();
            // Randomly select the new target point from the candidates
            Vector3 newTargetPoint = candidatePoints[_rnd.Next(0, candidatePoints.Count)];
            // Set the agent to go to the currently selected target
            _navMeshAgent.SetDestination(newTargetPoint);
            // Save the direction in which the agent will enter the new target
            _incomingDirection = GetIncomingDirection(_currentTargetPoint, newTargetPoint);
            // Save previous and new target points for next update
            _previousTargetPoint = _currentTargetPoint;
            _currentTargetPoint = newTargetPoint;
            // Retrieve next target points for debugging purposes
            _nextTargetPoints = GetCandidatePoints();
        }

        // Returns the points the agent may go to from its current target, relaxing the criteria one
        // at a time until at least one point remains:
        // 1. the visible points reachable without turning back, except the previous target;
        // 2. the visible points (e.g. at a dead end, where the agent has to turn back);
        // 3. any point but the current target.
        private List<Vector3> GetCandidatePoints() {
            List<Vector3> visiblePoints = GetVisiblePoints(_currentTargetPoint);

            List<Vector3> forwardPoints = visiblePoints
                .Where(point => point != _previousTargetPoint && !IsTurningBack(point))
                .ToList();

            if (forwardPoints.Count > 0) {
                return forwardPoints;
            }

            if (visiblePoints.Count > 0) {
                return visiblePoints;
            }

            return _targetPoints.Positions.Where(point => point != _currentTargetPoint).ToList();
        }

        private void DrawTargetPoints() {
            Transform transform = walker.transform;
            foreach (Vector3 targetPointPosition in _targetPoints.Positions) {
                Color targetPointColor = Color.black;
                if (targetPointPosition == _currentTargetPoint) {
                    targetPointColor = Color.green;
                }
                else if (targetPointPosition == _previousTargetPoint) {
                    targetPointColor = Color.blue;
                }
                else if (_nextTargetPoints.Contains(targetPointPosition)) {
                    targetPointColor = Color.yellow;
                }

                Debug.DrawRay(
                    targetPointPosition,
                    transform.up * config.targetPoints.height,
                    targetPointColor
                );
            }
        }

        private List<Vector3> GetVisiblePoints(Vector3 currentPoint) {
            return _targetPoints.Positions
                .Where(targetPointPosition =>
                    // Keep the point if it is not the current point itself,
                    targetPointPosition != currentPoint
                    // and the point is not hidden by an object,
                    && !Physics.Linecast(targetPointPosition, currentPoint, obstacleLayers)
                    // and the distance between the two points is more than the required tolerance
                    && Vector3.Distance(targetPointPosition, currentPoint) >=
                    config.remainingDistanceTolerance
                )
                .ToList();
        }

        // Whether the agent turns back to go from its current target to a point, i.e. the angle
        // between the directions in which it enters and leaves the current target exceeds the
        // maximum turn angle (never true if either direction is unknown, the angle being then zero)
        private bool IsTurningBack(Vector3 point) {
            Vector3 outgoingDirection = GetOutgoingDirection(_currentTargetPoint, point);
            return Vector3.Angle(_incomingDirection, outgoingDirection) > config.maxTurnAngle;
        }

        // Direction in which an agent enters a point, coming from another one, or zero if unknown
        private static Vector3 GetIncomingDirection(Vector3 from, Vector3 to) {
            Vector3[] corners = GetPathCorners(from, to);
            return corners.Length < 2 ? Vector3.zero : corners[^1] - corners[^2];
        }

        // Direction in which an agent leaves a point to reach another one, or zero if unknown
        private static Vector3 GetOutgoingDirection(Vector3 from, Vector3 to) {
            Vector3[] corners = GetPathCorners(from, to);
            return corners.Length < 2 ? Vector3.zero : corners[1] - corners[0];
        }

        // Returns the corners of the NavMesh path between two points (i.e. the points where it
        // turns, including both ends), or an empty array if there is no complete path
        private static Vector3[] GetPathCorners(Vector3 from, Vector3 to) {
            NavMeshPath path = new();
            bool isFound = NavMesh.CalculatePath(from, to, NavMesh.AllAreas, path);
            if (!isFound || path.status != NavMeshPathStatus.PathComplete) {
                return Array.Empty<Vector3>();
            }

            return path.corners;
        }
    }
}
