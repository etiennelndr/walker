using System;
using System.Collections.Generic;

using Api;
using Api.Models;

using UnityEngine;

using Ray = Api.Models.Ray;

namespace Agents {
    [Serializable]
    public class RaysConfig {
        [Min(1)] public int count = 8;
        [Min(0.5f)] public float maxDistance = 10f;
        public bool isVisible = true;

        [Min(1)] public int sendEveryNFrames = 1;
    }

    [Serializable]
    public abstract class BaseAgentConfig {
        public string serverUrl = "http://127.0.0.1:8000";
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
        protected readonly Walker walker;

        protected BaseAgent(TConfig config, Walker walker) {
            apiClient = new ApiClient(config.serverUrl);
            this.config = config;
            this.walker = walker;
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

        protected State CollectState() {
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

            return new State { collisions = collisions, speed = Velocity };
        }

        private RayCollision CastRay(Vector3 origin, Vector3 direction) {
            RaysConfig rays = config.rays;

            bool isHit = Physics.Raycast(origin, direction, out RaycastHit hit, rays.maxDistance);
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
