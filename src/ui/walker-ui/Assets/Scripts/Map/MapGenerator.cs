using System;
using System.Linq;

using Unity.AI.Navigation;

using UnityEngine;

using Random = UnityEngine.Random;

namespace Map {
    public class MapGenerator : MonoBehaviour {
        [SerializeField]
        [Tooltip("Settings of the streets and blocks of the map")]
        private MapLayoutConfig layoutConfig;

        [SerializeField]
        [Tooltip("Seed of the map, or 0 to draw a random one at each Play")]
        private int seed;

        [SerializeField]
        [Tooltip("Prefab of a wall, a cube of side 1 scaled to the size of each wall")]
        private GameObject wallPrefab;

        [SerializeField]
        [Min(1.5f)]
        [Tooltip("Height of the walls, above the 1 unit at which the walkers cast their rays")]
        private float wallHeight = 2f;

        [SerializeField]
        [Tooltip("NavMesh surface of the ground, resized to the map, rebuilt after the walls")]
        private NavMeshSurface groundSurface;

        [SerializeField]
        [Tooltip("Object that receives the target points of the map as children")]
        private TargetPoints targetPoints;

        [SerializeField]
        [Min(0.1f)]
        [Tooltip(
            "Height of the target points above the ground, below the walls so that they hide" +
            " the points from each other"
        )]
        private float targetPointHeight = 1f;

        public int Seed { get; private set; }
        public MapLayout Layout { get; private set; }

        private void Awake() {
            Seed = seed != 0 ? seed : Random.Range(1, int.MaxValue);
            Debug.Log($"Assigning seed {Seed} to the map", this);

            Layout = new MapLayout(layoutConfig, Seed);
            foreach (RectInt wall in Layout.Blocks.Concat(Layout.BorderWalls)) {
                CreateWall(wall);
            }

            foreach (Vector2 targetPointPosition in Layout.TargetPointPositions) {
                CreateTargetPoint(targetPointPosition);
            }

            // Make the ground cover the whole map, with its top at y = 0, at the foot of the walls.
            // It is 1 unit thick, so its center must be 0.5 below its top.
            groundSurface.transform.localPosition = new Vector3(
                layoutConfig.width / 2f,
                -0.5f,
                layoutConfig.depth / 2f
            );
            groundSurface.transform.localScale = new Vector3(
                layoutConfig.width,
                1,
                layoutConfig.depth
            );
            groundSurface.BuildNavMesh();
        }

        private void OnValidate() {
            try {
                layoutConfig.Validate();
            }
            catch (InvalidOperationException e) {
                Debug.LogError(e.Message, this);
            }
        }

        private void CreateWall(RectInt area) {
            GameObject wall = Instantiate(wallPrefab, transform);
            wall.name = $"Wall {area}";
            Vector2 wallCenter = area.center;
            float wallCenterHeight = wallHeight / 2f;
            wall.transform.localPosition = new Vector3(
                wallCenter.x,
                wallCenterHeight,
                wallCenter.y
            );
            wall.transform.localScale = new Vector3(
                area.width,
                wallHeight,
                area.height
            );
        }

        private void CreateTargetPoint(Vector2 position) {
            GameObject targetPoint = new($"TargetPoint {position}");
            targetPoint.transform.SetParent(
                targetPoints.transform,
                // Keep the local position, rotation and scale of the point, not the world ones
                false
            );
            targetPoint.transform.localPosition = new Vector3(
                position.x,
                targetPointHeight,
                position.y
            );
        }
    }
}
