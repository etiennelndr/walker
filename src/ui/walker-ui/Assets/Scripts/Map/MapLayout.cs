using System;
using System.Collections.Generic;
using System.Linq;

using UnityEngine;

using Random = System.Random;

namespace Map {
    [Serializable]
    public class MapLayoutConfig {
        [Min(30)]
        [Tooltip("Size of the map along the x-axis, in Unity units")]
        public int width = 60;

        [Min(30)]
        [Tooltip("Size of the map along the z-axis, in Unity units")]
        public int depth = 60;

        [Min(2)]
        [Tooltip("Smallest width of a street")]
        public int minStreetWidth = 3;

        [Min(2)]
        [Tooltip("Largest width of a street")]
        public int maxStreetWidth = 7;

        [Min(1)]
        [Tooltip("Smallest side of a block")]
        public int minBlockSize = 6;

        [Min(1)]
        [Tooltip("Largest side of a block")]
        public int maxBlockSize = 20;

        [Min(1)]
        [Tooltip("Thickness of the walls along the edges of the map, inside it")]
        public int borderWallThickness = 1;

        [Range(0f, 1f)]
        [Tooltip("Probability that an area which could still be split becomes a block")]
        public float blockProbability = 0.3f;

        [Range(0f, 1f)]
        [Tooltip("Probability that a block is removed to leave an open square")]
        public float plazaProbability = 0.1f;

        // A split needs room for two blocks and the street between them
        public int SmallestSplitSize => (2 * minBlockSize) + minStreetWidth;

        public void Validate() {
            if (maxStreetWidth < minStreetWidth) {
                throw new InvalidOperationException(
                    $"{nameof(maxStreetWidth)} must be greater than or equal to" +
                    $" {nameof(minStreetWidth)}"
                );
            }

            if (maxBlockSize < minBlockSize) {
                throw new InvalidOperationException(
                    $"{nameof(maxBlockSize)} must be greater than or equal to" +
                    $" {nameof(minBlockSize)}"
                );
            }

            if (maxBlockSize + 1 < SmallestSplitSize) {
                throw new InvalidOperationException(
                    $"{nameof(maxBlockSize)} must be at least {SmallestSplitSize - 1}" +
                    $" (2 * {nameof(minBlockSize)} + {nameof(minStreetWidth)} - 1), so that an" +
                    $" area larger than a block can always be split, but is {maxBlockSize}"
                );
            }

            // A street is at least minBlockSize from the edges, so thicker walls could cover it
            if (borderWallThickness > minBlockSize) {
                throw new InvalidOperationException(
                    $"{nameof(borderWallThickness)} must be at most {nameof(minBlockSize)}" +
                    $" ({minBlockSize}), so that the border walls never cover a street, but is" +
                    $" {borderWallThickness}"
                );
            }

            // Otherwise, the whole map would be a single block, without any street
            if (Math.Max(width, depth) < SmallestSplitSize) {
                throw new InvalidOperationException(
                    $"{nameof(width)} or {nameof(depth)} must be at least {SmallestSplitSize}" +
                    $" (2 * {nameof(minBlockSize)} + {nameof(minStreetWidth)}), so that the map" +
                    $" can be split at least once, but they are {width} and {depth}"
                );
            }
        }
    }

    public class MapLayout {
        private readonly List<RectInt> _blocks;
        private readonly MapLayoutConfig _config;
        private readonly List<RectInt> _plazas;
        private readonly Random _rnd;
        private readonly List<RectInt> _streetsAlongX;
        private readonly List<RectInt> _streetsAlongZ;

        public MapLayout(MapLayoutConfig config, int seed) {
            // Ensure configuration is valid before storing it to avoid storing an invalid one
            config.Validate();

            _config = config;
            _rnd = new Random(seed);
            _blocks = new List<RectInt>();
            _plazas = new List<RectInt>();
            _streetsAlongX = new List<RectInt>();
            _streetsAlongZ = new List<RectInt>();

            Seed = seed;

            RectInt area = new(0, 0, config.width, config.depth);
            SplitIntoBlocks(area);
            TurnBlocksIntoPlazas();

            TargetPointPositions = FindStreetJunctions()
                .Concat(FindStreetEndsOnBorder())
                // Two streets ending face to face on the same street give the same junction twice
                .Distinct()
                .ToList();
        }

        public IReadOnlyList<RectInt> Blocks => _blocks;

        public IReadOnlyList<RectInt> Plazas => _plazas;

        public IReadOnlyList<RectInt> Streets => _streetsAlongX.Concat(_streetsAlongZ).ToList();

        public IReadOnlyList<Vector2> TargetPointPositions { get; }

        public RectInt BottomWall => new(
            0,
            0,
            _config.width,
            _config.borderWallThickness
        );

        public RectInt TopWall => new(
            0,
            _config.depth - _config.borderWallThickness,
            _config.width,
            _config.borderWallThickness
        );

        public RectInt LeftWall => new(
            0,
            0,
            _config.borderWallThickness,
            _config.depth
        );

        public RectInt RightWall => new(
            _config.width - _config.borderWallThickness,
            0,
            _config.borderWallThickness,
            _config.depth
        );

        public RectInt[] BorderWalls => new[] { BottomWall, TopWall, LeftWall, RightWall };

        public int Seed { get; }

        private void SplitIntoBlocks(RectInt area) {
            if (ShouldBecomeBlock(area)) {
                _blocks.Add(area);
                return;
            }

            bool splitWidth = area.width > area.height;
            bool isSplitSuccessful = TrySplitByStreet(
                area,
                splitWidth,
                out RectInt firstArea,
                out RectInt street,
                out RectInt secondArea
            ) || TrySplitByStreet(
                area,
                !splitWidth,
                out firstArea,
                out street,
                out secondArea
            );

            if (isSplitSuccessful) {
                // A street along z spans the whole depth of the area it splits
                if (street.height == area.height) {
                    _streetsAlongZ.Add(street);
                }
                else {
                    _streetsAlongX.Add(street);
                }

                SplitIntoBlocks(firstArea);
                SplitIntoBlocks(secondArea);
            }
            else {
                _blocks.Add(area);
            }
        }

        private bool ShouldBecomeBlock(RectInt area) {
            // The main area must always be split
            if (area.width == _config.width && area.height == _config.depth) {
                return false;
            }

            // An area larger than a block must always be split
            if (area.width > _config.maxBlockSize || area.height > _config.maxBlockSize) {
                return false;
            }

            return _rnd.NextDouble() < _config.blockProbability;
        }

        // Tries to split an area in two sub-areas, separated by a street of random width, each one
        // keeping at least the smallest side of a block. The street is aligned with a parallel
        // street when there is one close enough. If splitWidth is true, the width of the area is
        // split and the street runs along the z-axis. Otherwise, its depth is split and the street
        // runs along the x-axis. Returns false, with default areas, if the area is too small to be
        // split this way.
        private bool TrySplitByStreet(
            RectInt area,
            bool splitWidth,
            out RectInt firstArea,
            out RectInt street,
            out RectInt secondArea
        ) {
            int splitLength = splitWidth ? area.width : area.height;

            if (splitLength < _config.SmallestSplitSize) {
                firstArea = default;
                street = default;
                secondArea = default;
                return false;
            }

            int streetWidth = RandomInt(
                _config.minStreetWidth,
                Math.Min(_config.maxStreetWidth, splitLength - (2 * _config.minBlockSize))
            );

            int firstAreaLength = RandomInt(
                _config.minBlockSize,
                splitLength - streetWidth - _config.minBlockSize
            );

            // Align the street with a close parallel one, so that streets facing each other form a
            // crossing
            bool isStreetToAlignWithFound = TryFindStreetToAlignWith(
                area,
                splitWidth,
                firstAreaLength,
                streetWidth,
                out RectInt streetToAlignWith
            );
            if (isStreetToAlignWithFound) {
                int streetToAlignWithStart = GetSplitStart(streetToAlignWith, splitWidth);
                firstAreaLength = streetToAlignWithStart - GetSplitStart(area, splitWidth);
                streetWidth = GetSplitEnd(streetToAlignWith, splitWidth) - streetToAlignWithStart;
            }

            int secondAreaLength = splitLength - streetWidth - firstAreaLength;

            firstArea = GetSubArea(area, splitWidth, 0, firstAreaLength);
            street = GetSubArea(area, splitWidth, firstAreaLength, streetWidth);
            secondArea = GetSubArea(
                area,
                splitWidth,
                firstAreaLength + streetWidth,
                secondAreaLength
            );

            return true;
        }

        // Returns the sub-area of an area that starts at the given offset along its split side and
        // has the given size on that side, keeping the other side of the area
        private static RectInt GetSubArea(RectInt area, bool splitWidth, int start, int size) {
            return splitWidth
                ? new RectInt(area.x + start, area.y, size, area.height)
                : new RectInt(area.x, area.y + start, area.width, size);
        }

        // Tries to find an existing street parallel to the new street, which starts at the given
        // offset in the area and has the given width. The two sides of a street are split
        // independently, so the streets that end on it from each side are rarely in line. Their
        // junctions then give target points very close to each other. Aligning the new street with
        // a close parallel street turns these junctions into a single crossing. The parallel street
        // must be closer than a block to the new street, and leave room for a block on each side of
        // it within the area. Returns false, with a default street, if there is none.
        private bool TryFindStreetToAlignWith(
            RectInt area,
            bool splitWidth,
            int start,
            int width,
            out RectInt streetToAlignWith
        ) {
            int areaStart = GetSplitStart(area, splitWidth);
            int areaEnd = GetSplitEnd(area, splitWidth);
            int streetStart = areaStart + start;
            int streetEnd = streetStart + width;

            foreach (RectInt parallelStreet in splitWidth ? _streetsAlongZ : _streetsAlongX) {
                int parallelStreetStart = GetSplitStart(parallelStreet, splitWidth);
                int parallelStreetEnd = GetSplitEnd(parallelStreet, splitWidth);

                // Distance between the two streets along the split side, negative when they overlap
                int gap = Math.Max(
                    parallelStreetStart - streetEnd,
                    streetStart - parallelStreetEnd
                );
                // Once aligned, the new street must keep a block on each side of it
                bool hasRoomForBlocks = parallelStreetStart - areaStart >= _config.minBlockSize &&
                    areaEnd - parallelStreetEnd >= _config.minBlockSize;

                if (gap < _config.minBlockSize && hasRoomForBlocks) {
                    streetToAlignWith = parallelStreet;
                    return true;
                }
            }

            streetToAlignWith = default;
            return false;
        }

        private static int GetSplitStart(RectInt area, bool splitWidth) {
            return splitWidth ? area.xMin : area.yMin;
        }

        private static int GetSplitEnd(RectInt area, bool splitWidth) {
            return splitWidth ? area.xMax : area.yMax;
        }

        private void TurnBlocksIntoPlazas() {
            foreach (RectInt block in _blocks) {
                if (ShouldBecomePlaza()) {
                    _plazas.Add(block);
                }
            }

            // Blocks never overlap, so each plaza matches exactly one block
            _blocks.RemoveAll(_plazas.Contains);
        }

        private bool ShouldBecomePlaza() {
            return _rnd.NextDouble() < _config.plazaProbability;
        }

        private IEnumerable<Vector2> FindStreetJunctions() {
            foreach (RectInt streetAlongZ in _streetsAlongZ) {
                // Overlaps ignores rectangles that only touch, so grow the street by 1 on each side
                RectInt grownStreetAlongZ = new(
                    streetAlongZ.x - 1,
                    streetAlongZ.y - 1,
                    streetAlongZ.width + 2,
                    streetAlongZ.height + 2
                );
                foreach (RectInt streetAlongX in _streetsAlongX) {
                    if (grownStreetAlongZ.Overlaps(streetAlongX)) {
                        yield return new Vector2(streetAlongZ.center.x, streetAlongX.center.y);
                    }
                }
            }
        }

        // Returns a point at the center of the end of each street that reaches the border
        private IEnumerable<Vector2> FindStreetEndsOnBorder() {
            // Place each point at the center of the end of its street, as a junction is at its
            // center
            foreach (RectInt streetAlongX in _streetsAlongX) {
                float distanceToEdge = _config.borderWallThickness + (streetAlongX.height / 2f);

                if (streetAlongX.xMin == 0) {
                    yield return new Vector2(distanceToEdge, streetAlongX.center.y);
                }

                if (streetAlongX.xMax == _config.width) {
                    yield return new Vector2(_config.width - distanceToEdge, streetAlongX.center.y);
                }
            }

            foreach (RectInt streetAlongZ in _streetsAlongZ) {
                float distanceToEdge = _config.borderWallThickness + (streetAlongZ.width / 2f);

                if (streetAlongZ.yMin == 0) {
                    yield return new Vector2(streetAlongZ.center.x, distanceToEdge);
                }

                if (streetAlongZ.yMax == _config.depth) {
                    yield return new Vector2(streetAlongZ.center.x, _config.depth - distanceToEdge);
                }
            }
        }

        // Returns a random integer between min and max, both included
        private int RandomInt(int min, int max) {
            return _rnd.Next(min, max + 1);
        }
    }
}
