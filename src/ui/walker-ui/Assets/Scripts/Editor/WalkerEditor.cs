using System;

using UnityEditor;

// Must stay in an "Editor" folder: UnityEditor is not available in builds.
namespace Editor {
    [CustomEditor(typeof(Walker))]
    public class WalkerEditor : UnityEditor.Editor {
        // Only what is drawn here is displayed: any new field of Walker must be added explicitly.
        public override void OnInspectorGUI() {
            serializedObject.Update();

            // Fields are looked up by name: keep these strings in sync with the field names of
            // Walker, a mismatch does not fail at compile time.
            SerializedProperty behaviour = serializedObject.FindProperty("behaviour");
            EditorGUILayout.PropertyField(behaviour);

            string configName = (WalkerBehaviour)behaviour.enumValueIndex switch {
                WalkerBehaviour.Training => "trainingAgentConfig",
                WalkerBehaviour.Patrolling => "patrollingAgentConfig",
                _ => throw new ArgumentOutOfRangeException()
            };

            EditorGUILayout.PropertyField(
                serializedObject.FindProperty(configName),
                // true: also draw the fields of the config
                true
            );
            // Without this call, the values edited in the Inspector are lost
            serializedObject.ApplyModifiedProperties();
        }
    }
}
