using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace Api.Models {
    public abstract class ApiModel<TSelf> where TSelf : ApiModel<TSelf> {
        // The API names its fields in snake_case, which are converted from and to the C# naming of
        // the models. Fields left empty are not sent.
        private static readonly JsonSerializerSettings JsonSettings = new() {
            ContractResolver = new DefaultContractResolver {
                NamingStrategy = new SnakeCaseNamingStrategy()
            },
            NullValueHandling = NullValueHandling.Ignore
        };

        public string Encode() {
            return JsonConvert.SerializeObject(this, JsonSettings);
        }

        public static TSelf Decode(string json) {
            return JsonConvert.DeserializeObject<TSelf>(json, JsonSettings);
        }
    }
}
