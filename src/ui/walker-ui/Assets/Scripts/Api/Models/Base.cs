using System;

using UnityEngine;

namespace Api.Models {
    [Serializable]
    public abstract class ApiModel<TSelf> where TSelf : ApiModel<TSelf> {
        public string Encode() {
            return JsonUtility.ToJson(this);
        }

        public static TSelf Decode(string json) {
            return JsonUtility.FromJson<TSelf>(json);
        }
    }
}
