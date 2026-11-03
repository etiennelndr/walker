using System;
using System.Collections.Generic;

using Api;
using Api.Models;

using Map;

using UnityEngine;

using Object = UnityEngine.Object;
using Ray = Api.Models.Ray;
using Vector3 = UnityEngine.Vector3;

namespace Agents {
    [Serializable]
    public class RaysConfig {
        [Min(1)]
        [Tooltip("Number of rays cast around the walker, evenly spread")]
        public int count = 32;

        [Min(0.5f)]
        [Tooltip("Largest distance at which a ray detects an obstacle, in Unity units")]
        public float maxDistance = 10f;

        [Tooltip("Whether the rays are drawn in the Scene view")]
        public bool isVisible = true;

        [Min(1)]
        [Tooltip("Number of frames between two records sent to the API")]
        public int sendEveryNFrames = 1;
    }

    [Serializable]
    public abstract class BaseAgentConfig {
        [Tooltip("URL of the API that receives the records")]
        public string serverUrl = "http://127.0.0.1:8000";

        [Tooltip("Settings of the rays with which the walker observes its surroundings")]
        public RaysConfig rays;
    }

    public abstract class BaseAgent {
        protected abstract Vector3 Velocity {
            get;
        }

        public abstract void Init();
        public abstract void Step();
    }

    public abstract class BaseAgent<TConfig> : BaseAgent where TConfig : BaseAgentConfig {
        protected readonly ApiClient apiClient;
        protected readonly TConfig config;
        protected readonly MapGenerator mapGenerator;
        protected readonly int obstacleLayers;
        protected readonly Walker walker;

        protected BaseAgent(TConfig config, Walker walker) {
            this.config = config;
            this.walker = walker;

            mapGenerator = Object.FindAnyObjectByType<MapGenerator>();
            obstacleLayers = Physics.DefaultRaycastLayers & ~LayerMask.GetMask("Walker");
            apiClient = new ApiClient(config.serverUrl);
        }

        protected virtual void Enable(string reason) {
            if (!walker) {
                return;
            }

            Debug.Log(reason, walker);
            walker.enabled = true;
        }

        protected virtual void Disable(string reason) {
            if (!walker) {
                return;
            }

            Debug.Log(reason, walker);
            walker.enabled = false;
        }

        protected virtual Record CollectRecord() {
            return new Record {
                session = Session.Id,
                walker = walker.name,
                scene = walker.gameObject.scene.name,
                mapSeed = mapGenerator.Seed,
                frame = Time.frameCount,
                time = Time.time,
                observation = CollectObservation()
            };
        }

        protected Observation CollectObservation() {
            RaysConfig rays = config.rays;
            Transform walkerTransform = walker.transform;
            Vector3 origin = walkerTransform.position;
            Vector3 forward = walkerTransform.forward;

            List<RayCollision> collisions = new(rays.count);
            for (int i = 0; i < rays.count; i++) {
                float angle = i * 360f / rays.count;
                Vector3 direction = Quaternion.AngleAxis(angle, Vector3.up) * forward;
                RayCollision rayCollision = CastRay(origin, direction);
                collisions.Add(rayCollision);
            }

            return new Observation { collisions = collisions, velocity = Velocity };
        }

        private RayCollision CastRay(Vector3 origin, Vector3 direction) {
            RaysConfig rays = config.rays;

            bool isHit = Physics.Raycast(
                origin,
                direction,
                out RaycastHit hit,
                rays.maxDistance,
                obstacleLayers
            );
            // A ray that hits nothing still produces a collision, located at its maximum distance
            Vector3 point = isHit ? hit.point : origin + (direction * rays.maxDistance);

            if (rays.isVisible) {
                Debug.DrawLine(origin, point, isHit ? Color.yellow : Color.white);
            }

            Ray ray = new() { origin = origin, direction = direction };
            return new RayCollision { ray = ray, point = point };
        }
    }
}
